#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk
import subprocess
import threading
import queue
import numpy as np
import time


# ============================================================
# REAL-TIME SPEECH ENHANCEMENT
# Fedora + PipeWire + LMS Adaptive Noise Cancellation
# ============================================================

SAMPLE_RATE = 48000
CHANNELS = 1
BLOCK_SIZE = 4800          # 100 ms
FILTER_LENGTH = 64
MU = 0.00005

VIRTUAL_SINK = "speech_enhanced"


# ============================================================
# FEDORA MICROPHONES
#
# Mic2 = PRIMARY SPEECH MICROPHONE
# Mic1 = NOISE REFERENCE MICROPHONE
# ============================================================

PRIMARY_SOURCE = (
    "alsa_input.pci-0000_04_00.6.HiFi__Mic2__source"
)

REFERENCE_SOURCE = (
    "alsa_input.pci-0000_04_00.6.HiFi__Mic1__source"
)


# ============================================================
# GLOBAL VARIABLES
# ============================================================

running = False

primary_process = None
reference_process = None
output_process = None

processing_thread = None

audio_queue = queue.Queue(maxsize=10)

status_text = "Stopped"

input_level = 0.0
output_level = 0.0


# ============================================================
# LMS ADAPTIVE NOISE CANCELLER
# ============================================================

class LMSNoiseCanceller:

    def __init__(self, filter_length, mu):

        self.filter_length = filter_length
        self.mu = mu

        self.weights = np.zeros(
            filter_length,
            dtype=np.float64
        )

        self.reference_buffer = np.zeros(
            filter_length,
            dtype=np.float64
        )

    def process(self, primary, reference):

        primary = np.asarray(
            primary,
            dtype=np.float64
        )

        reference = np.asarray(
            reference,
            dtype=np.float64
        )

        output = np.zeros_like(primary)

        for n in range(len(primary)):

            # ------------------------------------------------
            # Shift reference samples
            # ------------------------------------------------

            self.reference_buffer[1:] = (
                self.reference_buffer[:-1]
            )

            self.reference_buffer[0] = reference[n]

            # ------------------------------------------------
            # Estimate noise
            # ------------------------------------------------

            estimated_noise = np.dot(
                self.weights,
                self.reference_buffer
            )

            # ------------------------------------------------
            # Error signal
            # ------------------------------------------------

            error = (
                primary[n]
                - estimated_noise
            )

            # ------------------------------------------------
            # LMS weight update
            # ------------------------------------------------

            self.weights += (
                2.0
                * self.mu
                * error
                * self.reference_buffer
            )

            # ------------------------------------------------
            # Enhanced output
            # ------------------------------------------------

            output[n] = error

        return output


lms = LMSNoiseCanceller(
    FILTER_LENGTH,
    MU
)


# ============================================================
# PIPEWIRE CHECK
# ============================================================

def check_virtual_sink():

    try:

        result = subprocess.run(
            [
                "pactl",
                "list",
                "short",
                "sinks"
            ],
            capture_output=True,
            text=True
        )

        return VIRTUAL_SINK in result.stdout

    except Exception as error:

        print(
            "PipeWire check error:",
            error
        )

        return False


# ============================================================
# CREATE VIRTUAL SINK IF NEEDED
# ============================================================

def create_virtual_sink():

    if check_virtual_sink():

        print(
            "Virtual sink already exists:",
            VIRTUAL_SINK
        )

        return True

    print(
        "Creating PipeWire virtual sink..."
    )

    try:

        result = subprocess.run(
            [
                "pactl",
                "load-module",
                "module-null-sink",
                f"sink_name={VIRTUAL_SINK}",
                'sink_properties=device.description="Speech_Enhanced_Virtual_Mic"'
            ],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:

            print(
                "Could not create virtual sink:"
            )

            print(
                result.stderr
            )

            return False

        time.sleep(0.2)

        return True

    except Exception as error:

        print(
            "Virtual sink creation error:",
            error
        )

        return False


# ============================================================
# START MICROPHONE CAPTURE
# ============================================================

def start_capture(source):

    command = [
        "parec",

        "--device",
        source,

        "--format=float32le",

        f"--rate={SAMPLE_RATE}",

        f"--channels={CHANNELS}",

        "--latency-msec=50"
    ]

    print(
        "Starting capture:"
    )

    print(
        " ".join(command)
    )

    return subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=0
    )


# ============================================================
# START OUTPUT TO PIPEWIRE
# ============================================================

def start_output():

    command = [
        "pw-cat",

        "--playback",

        "--target",
        VIRTUAL_SINK,

        # IMPORTANT:
        # The audio generated by Python is raw PCM data.
        "--raw",

        "--format",
        "f32",

        "--rate",
        str(SAMPLE_RATE),

        "--channels",
        str(CHANNELS),

        "--latency",
        "100/48000",

        # IMPORTANT:
        # "-" means read raw audio from stdin.
        "-"
    ]

    print(
        "Starting output:"
    )

    print(
        " ".join(command)
    )

    return subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=0
    )


# ============================================================
# READ PROCESS ERROR
# ============================================================

def read_process_error(process):

    try:

        if process is not None and process.stderr:

            data = process.stderr.read()

            if data:

                return data.decode(
                    errors="replace"
                ).strip()

    except Exception:

        pass

    return ""


# ============================================================
# AUDIO PROCESSING THREAD
# ============================================================

def processing_loop():

    global running
    global input_level
    global output_level

    bytes_per_block = (
        BLOCK_SIZE * 4
    )

    print(
        "Audio processing thread started."
    )

    while running:

        try:

            # =================================================
            # CHECK AUDIO PROCESSES
            # =================================================

            if (
                primary_process is None
                or reference_process is None
                or output_process is None
            ):

                print(
                    "Audio process is not available."
                )

                running = False

                root.after(
                    0,
                    lambda: update_status("Error")
                )

                break

            # =================================================
            # CHECK PW-CAT
            # =================================================

            if output_process.poll() is not None:

                print(
                    "pw-cat output process has stopped."
                )

                error_text = read_process_error(
                    output_process
                )

                if error_text:

                    print(
                        "pw-cat error:"
                    )

                    print(
                        error_text
                    )

                running = False

                root.after(
                    0,
                    lambda: update_status("Error")
                )

                break

            # =================================================
            # READ PRIMARY MICROPHONE
            # =================================================

            primary_bytes = (
                primary_process.stdout.read(
                    bytes_per_block
                )
            )

            # =================================================
            # READ NOISE REFERENCE
            # =================================================

            reference_bytes = (
                reference_process.stdout.read(
                    bytes_per_block
                )
            )

            # =================================================
            # CHECK STREAMS
            # =================================================

            if not primary_bytes:

                print(
                    "Primary microphone stream ended."
                )

                running = False

                root.after(
                    0,
                    lambda: update_status("Error")
                )

                break

            if not reference_bytes:

                print(
                    "Noise reference stream ended."
                )

                running = False

                root.after(
                    0,
                    lambda: update_status("Error")
                )

                break

            # =================================================
            # CONVERT TO FLOAT32
            # =================================================

            primary = np.frombuffer(
                primary_bytes,
                dtype=np.float32
            ).copy()

            reference = np.frombuffer(
                reference_bytes,
                dtype=np.float32
            ).copy()

            # =================================================
            # MATCH LENGTH
            # =================================================

            length = min(
                len(primary),
                len(reference)
            )

            primary = primary[:length]
            reference = reference[:length]

            if length == 0:

                continue

            # =================================================
            # INPUT LEVEL
            # =================================================

            input_level = float(
                np.sqrt(
                    np.mean(
                        primary ** 2
                    )
                )
            )

            # =================================================
            # LMS NOISE CANCELLATION
            # =================================================

            enhanced = lms.process(
                primary,
                reference
            )

            # =================================================
            # REMOVE DC COMPONENT
            # =================================================

            enhanced -= np.mean(
                enhanced
            )

            # =================================================
            # SAFETY LIMITER
            # =================================================

            peak = np.max(
                np.abs(enhanced)
            )

            if peak > 0.95:

                enhanced *= (
                    0.95 / peak
                )

            # =================================================
            # OUTPUT LEVEL
            # =================================================

            output_level = float(
                np.sqrt(
                    np.mean(
                        enhanced ** 2
                    )
                )
            )

            # =================================================
            # CONVERT TO RAW FLOAT32
            # =================================================

            enhanced_bytes = (
                enhanced
                .astype(np.float32)
                .tobytes()
            )

            # =================================================
            # SEND TO PW-CAT
            # =================================================

            output_process.stdin.write(
                enhanced_bytes
            )

            output_process.stdin.flush()

        # =====================================================
        # BROKEN PIPE
        # =====================================================

        except BrokenPipeError:

            if running:

                print(
                    "Processing error: "
                    "pw-cat closed the input pipe."
                )

                error_text = read_process_error(
                    output_process
                )

                if error_text:

                    print(
                        "pw-cat error:"
                    )

                    print(
                        error_text
                    )

                running = False

                root.after(
                    0,
                    lambda: update_status("Error")
                )

            break

        # =====================================================
        # GENERAL ERROR
        # =====================================================

        except Exception as error:

            if running:

                print(
                    "Processing error:",
                    error
                )

                running = False

                root.after(
                    0,
                    lambda: update_status("Error")
                )

            break

    print(
        "Audio processing thread stopped."
    )


# ============================================================
# START SYSTEM
# ============================================================

def start_processing():

    global running
    global primary_process
    global reference_process
    global output_process
    global processing_thread
    global lms

    if running:

        return

    print()
    print("=" * 60)
    print("REAL-TIME SPEECH ENHANCEMENT")
    print("=" * 60)

    # ========================================================
    # RESET LMS FILTER
    # ========================================================

    lms = LMSNoiseCanceller(
        FILTER_LENGTH,
        MU
    )

    # ========================================================
    # CREATE / CHECK VIRTUAL SINK
    # ========================================================

    if not create_virtual_sink():

        root.after(
            0,
            lambda: update_status(
                "Virtual microphone error"
            )
        )

        return

    # ========================================================
    # START AUDIO PROCESSES
    # ========================================================

    try:

        # ----------------------------------------------------
        # PRIMARY MICROPHONE
        # ----------------------------------------------------

        primary_process = start_capture(
            PRIMARY_SOURCE
        )

        print(
            "Primary microphone:",
            PRIMARY_SOURCE
        )

        # ----------------------------------------------------
        # NOISE REFERENCE
        # ----------------------------------------------------

        reference_process = start_capture(
            REFERENCE_SOURCE
        )

        print(
            "Noise reference:",
            REFERENCE_SOURCE
        )

        # ----------------------------------------------------
        # OUTPUT
        # ----------------------------------------------------

        output_process = start_output()

        # ----------------------------------------------------
        # CHECK PW-CAT
        # ----------------------------------------------------

        time.sleep(0.2)

        if output_process.poll() is not None:

            error_text = read_process_error(
                output_process
            )

            if error_text:

                raise RuntimeError(
                    "pw-cat exited unexpectedly:\n"
                    + error_text
                )

            raise RuntimeError(
                "pw-cat exited unexpectedly."
            )

        print(
            "Virtual output:",
            VIRTUAL_SINK
        )

        # ====================================================
        # START PROCESSING
        # ====================================================

        running = True

        root.after(
            0,
            lambda: update_status("Running")
        )

        processing_thread = threading.Thread(
            target=processing_loop,
            daemon=True
        )

        processing_thread.start()

        print()
        print(
            "Processing started."
        )

        print(
            "Speak into your microphone."
        )

        print()

        print(
            "Meeting microphone:"
        )

        print(
            "Speech_Enhanced_Virtual_Mic Monitor"
        )

        print()

        root.after(
            0,
            update_meter
        )

    except Exception as error:

        print(
            "START ERROR:",
            error
        )

        stop_processing()


# ============================================================
# STOP SYSTEM
# ============================================================

def stop_processing():

    global running
    global primary_process
    global reference_process
    global output_process
    global input_level
    global output_level

    running = False

    print(
        "\nStopping real-time processing..."
    )

    # ========================================================
    # STOP AUDIO PROCESSES
    # ========================================================

    processes = [
        primary_process,
        reference_process,
        output_process
    ]

    for process in processes:

        if process is None:

            continue

        # ----------------------------------------------------
        # Close stdin
        # ----------------------------------------------------

        try:

            if process.stdin:

                process.stdin.close()

        except Exception:

            pass

        # ----------------------------------------------------
        # Terminate process
        # ----------------------------------------------------

        try:

            process.terminate()

        except Exception:

            pass

        # ----------------------------------------------------
        # Wait
        # ----------------------------------------------------

        try:

            process.wait(
                timeout=1
            )

        except Exception:

            try:

                process.kill()

            except Exception:

                pass

    # ========================================================
    # RESET PROCESSES
    # ========================================================

    primary_process = None
    reference_process = None
    output_process = None

    # ========================================================
    # RESET LEVELS
    # ========================================================

    input_level = 0.0
    output_level = 0.0

    # ========================================================
    # UPDATE GUI
    # ========================================================

    try:

        root.after(
            0,
            lambda: update_status("Stopped")
        )

    except Exception:

        pass

    print(
        "Processing stopped."
    )


# ============================================================
# GUI STATUS
# ============================================================

def update_status(text=None):

    global status_text

    if text is not None:

        status_text = text

    try:

        status_label.config(
            text="Status: " + status_text
        )

    except Exception:

        pass


# ============================================================
# AUDIO METERS
# ============================================================

def update_meter():

    if not running:

        input_progress["value"] = 0
        output_progress["value"] = 0

        return

    # ========================================================
    # INPUT LEVEL
    # ========================================================

    input_value = min(
        100,
        input_level * 500
    )

    # ========================================================
    # OUTPUT LEVEL
    # ========================================================

    output_value = min(
        100,
        output_level * 500
    )

    input_progress["value"] = (
        input_value
    )

    output_progress["value"] = (
        output_value
    )

    # ========================================================
    # UPDATE EVERY 100 ms
    # ========================================================

    root.after(
        100,
        update_meter
    )


# ============================================================
# SHOW DEVICES
# ============================================================

def show_devices():

    print()
    print("=" * 60)
    print("PIPEWIRE AUDIO SOURCES")
    print("=" * 60)

    subprocess.run(
        [
            "pactl",
            "list",
            "short",
            "sources"
        ]
    )

    print()
    print("=" * 60)
    print("PIPEWIRE AUDIO SINKS")
    print("=" * 60)

    subprocess.run(
        [
            "pactl",
            "list",
            "short",
            "sinks"
        ]
    )

    print()


# ============================================================
# GUI
# ============================================================

root = tk.Tk()

root.title(
    "Real-Time Speech Enhancement"
)

root.geometry(
    "650x520"
)

root.resizable(
    False,
    False
)


# ============================================================
# TITLE
# ============================================================

title = tk.Label(
    root,
    text="Speech Enhancement & Noise Removal",
    font=("Arial", 20, "bold")
)

title.pack(
    pady=(25, 10)
)


# ============================================================
# SUBTITLE
# ============================================================

subtitle = tk.Label(
    root,
    text=(
        "Real-Time LMS Adaptive Noise Cancellation\n"
        "Fedora + PipeWire"
    ),
    font=("Arial", 12)
)

subtitle.pack(
    pady=5
)


# ============================================================
# STATUS
# ============================================================

status_label = tk.Label(
    root,
    text="Status: Stopped",
    font=("Arial", 14)
)

status_label.pack(
    pady=20
)


# ============================================================
# START / STOP BUTTONS
# ============================================================

button_frame = tk.Frame(
    root
)

button_frame.pack(
    pady=5
)


# ------------------------------------------------------------
# START
# ------------------------------------------------------------

start_button = ttk.Button(
    button_frame,
    text="START",
    command=lambda: threading.Thread(
        target=start_processing,
        daemon=True
    ).start()
)

start_button.grid(
    row=0,
    column=0,
    padx=10,
    ipadx=35,
    ipady=10
)


# ------------------------------------------------------------
# STOP
# ------------------------------------------------------------

stop_button = ttk.Button(
    button_frame,
    text="STOP",
    command=stop_processing
)

stop_button.grid(
    row=0,
    column=1,
    padx=10,
    ipadx=35,
    ipady=10
)


# ============================================================
# INPUT METER
# ============================================================

tk.Label(
    root,
    text="Microphone Input Level"
).pack(
    pady=(25, 5)
)


input_progress = ttk.Progressbar(
    root,
    length=450,
    maximum=100
)

input_progress.pack()


# ============================================================
# OUTPUT METER
# ============================================================

tk.Label(
    root,
    text="Enhanced Output Level"
).pack(
    pady=(20, 5)
)


output_progress = ttk.Progressbar(
    root,
    length=450,
    maximum=100
)

output_progress.pack()


# ============================================================
# DEVICE BUTTON
# ============================================================

device_button = ttk.Button(
    root,
    text="SHOW PIPEWIRE DEVICES",
    command=show_devices
)

device_button.pack(
    pady=25
)


# ============================================================
# INFORMATION
# ============================================================

info = tk.Label(
    root,
    text=(
        "Primary: Mic2\n"
        "Reference: Mic1\n"
        "Output: Speech_Enhanced_Virtual_Mic\n\n"
        "Use the virtual microphone as the input\n"
        "in your meeting application."
    ),
    font=("Arial", 10),
    justify="center"
)

info.pack(
    pady=5
)


# ============================================================
# CLOSE WINDOW
# ============================================================

def close_application():

    stop_processing()

    root.destroy()


root.protocol(
    "WM_DELETE_WINDOW",
    close_application
)


# ============================================================
# RUN
# ============================================================

root.mainloop()
