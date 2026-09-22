#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox

import importlib
import threading
import time
from pathlib import Path

import numpy as np
import soundfile as sf


# ============================================================
# SOUNDDEVICE
# ============================================================

try:
    sd = importlib.import_module("sounddevice")
except ImportError as error:
    sd = None
    _sounddevice_import_error = error


# ============================================================
# V4.1
# ============================================================

from spectral_noise_reduction_v41 import (
    SpectralNoiseReducer
)


# ============================================================
# PLOTS
# ============================================================

from plot_comparison_v41 import (
    create_waveform_plot,
    create_spectrogram_plot,
    create_metrics_plot
)


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_DIR = PROJECT_ROOT / "input"
OUTPUT_DIR = PROJECT_ROOT / "output"
PLOTS_DIR = PROJECT_ROOT / "plots"

INPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

PLOTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# AUDIO SETTINGS
# ============================================================

SAMPLE_RATE = 48000
TEST_DURATION = 30
BLOCK_SIZE = 2048
CHANNELS = 1

# This is the output level boost that was tested
# successfully with the standalone V4.1 processor.
OUTPUT_GAIN = 3.0


# ============================================================
# APPLICATION
# ============================================================

class SpeechEnhancementApp:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "Speech Enhancement and Noise Removal - V4.1"
        )

        self.root.geometry(
            "1100x760"
        )

        self.root.minsize(
            950,
            650
        )

        # ----------------------------------------------------
        # COLORS
        # ----------------------------------------------------

        self.bg = "#101318"
        self.card = "#181d24"
        self.card2 = "#202630"

        self.text = "#f2f4f7"
        self.muted = "#9ba5b1"

        self.accent = "#5eead4"
        self.green = "#4ade80"
        self.red = "#fb7185"
        self.blue = "#60a5fa"
        self.orange = "#fbbf24"

        self.root.configure(
            bg=self.bg
        )

        # ----------------------------------------------------
        # DEVICES
        # ----------------------------------------------------

        self.input_devices = []
        self.output_devices = []

        # ----------------------------------------------------
        # TEST DATA
        # ----------------------------------------------------

        self.test_original = None
        self.test_enhanced = None

        self.test_recording = False
        self.test_cancel = False

        self.playing = False

        # ----------------------------------------------------
        # MEETING DATA
        # ----------------------------------------------------

        self.meeting_stream = None
        self.meeting_thread = None

        self.meeting_running = False
        self.meeting_cancel = False

        self.live_reducer = None

        # ----------------------------------------------------
        # LEVELS
        # ----------------------------------------------------

        self.input_level = 0.0
        self.output_level = 0.0
        self.processing_ms = 0.0

        # ----------------------------------------------------
        # BUILD
        # ----------------------------------------------------

        self.build_style()
        self.build_ui()
        self.refresh_devices()

        self.root.after(
            100,
            self.update_meters
        )

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_app
        )

    # ========================================================
    # STYLE
    # ========================================================

    def build_style(self):

        style = ttk.Style()

        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            "TNotebook",
            background=self.bg,
            borderwidth=0
        )

        style.configure(
            "TNotebook.Tab",
            background=self.card2,
            foreground=self.muted,
            padding=(25, 12),
            font=(
                "DejaVu Sans",
                11,
                "bold"
            )
        )

        style.map(
            "TNotebook.Tab",
            background=[
                (
                    "selected",
                    self.card
                )
            ],
            foreground=[
                (
                    "selected",
                    self.accent
                )
            ]
        )

        style.configure(
            "TCombobox",
            fieldbackground=self.card2,
            background=self.card2,
            foreground=self.text,
            arrowcolor=self.accent
        )

        style.configure(
            "Horizontal.TProgressbar",
            troughcolor=self.card2,
            background=self.accent,
            borderwidth=0
        )

    # ========================================================
    # MAIN UI
    # ========================================================

    def build_ui(self):

        header = tk.Frame(
            self.root,
            bg=self.bg
        )

        header.pack(
            fill="x",
            padx=35,
            pady=(25, 5)
        )

        tk.Label(
            header,
            text="SPEECH ENHANCEMENT APP",
            font=(
                "DejaVu Sans",
                24,
                "bold"
            ),
            fg=self.text,
            bg=self.bg
        ).pack(
            anchor="w"
        )

        tk.Label(
            header,
            text=(
                "Real-Time Speech Enhancement "
                "• Phase 2 • V4.1"
            ),
            font=(
                "DejaVu Sans",
                11
            ),
            fg=self.muted,
            bg=self.bg
        ).pack(
            anchor="w",
            pady=(4, 0)
        )

        self.status_label = tk.Label(
            header,
            text="●  READY",
            font=(
                "DejaVu Sans",
                10,
                "bold"
            ),
            fg=self.green,
            bg=self.bg
        )

        self.status_label.pack(
            anchor="e"
        )

        # ----------------------------------------------------
        # NOTEBOOK
        # ----------------------------------------------------

        self.notebook = ttk.Notebook(
            self.root
        )

        self.notebook.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=20
        )

        self.test_tab = tk.Frame(
            self.notebook,
            bg=self.bg
        )

        self.meeting_tab = tk.Frame(
            self.notebook,
            bg=self.bg
        )

        self.notebook.add(
            self.test_tab,
            text="  TEST MODE  "
        )

        self.notebook.add(
            self.meeting_tab,
            text="  MEETING MODE  "
        )

        self.build_test_mode()
        self.build_meeting_mode()

    # ========================================================
    # MICROPHONE CARD
    # ========================================================

    def create_microphone_card(self, parent):

        card = tk.Frame(
            parent,
            bg=self.card,
            highlightbackground="#2a3039",
            highlightthickness=1
        )

        card.pack(
            fill="x",
            padx=20,
            pady=15
        )

        tk.Label(
            card,
            text="App Microphone",
            font=(
                "DejaVu Sans",
                13,
                "bold"
            ),
            fg=self.text,
            bg=self.card
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 5)
        )

        tk.Label(
            card,
            text=(
                "Physical microphone used by "
                "the application"
            ),
            font=(
                "DejaVu Sans",
                9
            ),
            fg=self.muted,
            bg=self.card
        ).pack(
            anchor="w",
            padx=20
        )

        combo = ttk.Combobox(
            card,
            state="readonly",
            font=(
                "DejaVu Sans",
                10
            )
        )

        combo.pack(
            fill="x",
            padx=20,
            pady=(10, 18)
        )

        return combo

    # ========================================================
    # TEST MODE
    # ========================================================

    def build_test_mode(self):

        self.test_mic_combo = (
            self.create_microphone_card(
                self.test_tab
            )
        )

        # ----------------------------------------------------
        # OUTPUT CARD
        # ----------------------------------------------------

        output_card = tk.Frame(
            self.test_tab,
            bg=self.card,
            highlightbackground="#2a3039",
            highlightthickness=1
        )

        output_card.pack(
            fill="x",
            padx=20,
            pady=5
        )

        tk.Label(
            output_card,
            text="Test Output",
            font=(
                "DejaVu Sans",
                13,
                "bold"
            ),
            fg=self.text,
            bg=self.card
        ).pack(
            anchor="w",
            padx=20,
            pady=(15, 5)
        )

        tk.Label(
            output_card,
            text=(
                "Speaker or headphones used "
                "for playback"
            ),
            font=(
                "DejaVu Sans",
                9
            ),
            fg=self.muted,
            bg=self.card
        ).pack(
            anchor="w",
            padx=20
        )

        self.test_output_combo = ttk.Combobox(
            output_card,
            state="readonly",
            font=(
                "DejaVu Sans",
                10
            )
        )

        self.test_output_combo.pack(
            fill="x",
            padx=20,
            pady=(10, 15)
        )

        # ----------------------------------------------------
        # TIMER
        # ----------------------------------------------------

        self.test_timer_label = tk.Label(
            self.test_tab,
            text="Ready for 30-second test",
            font=(
                "DejaVu Sans",
                12,
                "bold"
            ),
            fg=self.muted,
            bg=self.bg
        )

        self.test_timer_label.pack(
            pady=(15, 5)
        )

        # ----------------------------------------------------
        # BUTTONS
        # ----------------------------------------------------

        buttons = tk.Frame(
            self.test_tab,
            bg=self.bg
        )

        buttons.pack(
            fill="x",
            padx=20,
            pady=15
        )

        self.record_button = tk.Button(
            buttons,
            text="●  Record & Enhance",
            command=self.start_test,
            bg=self.accent,
            fg="#071312",
            activebackground=self.accent,
            font=(
                "DejaVu Sans",
                11,
                "bold"
            ),
            relief="flat",
            padx=22,
            pady=12,
            cursor="hand2"
        )

        self.record_button.pack(
            side="left",
            padx=5
        )

        self.cancel_test_button = tk.Button(
            buttons,
            text="■  Cancel Test",
            command=self.cancel_test,
            bg=self.card2,
            fg=self.text,
            activebackground="#303846",
            font=(
                "DejaVu Sans",
                10,
                "bold"
            ),
            relief="flat",
            padx=18,
            pady=12,
            cursor="hand2",
            state="disabled"
        )

        self.cancel_test_button.pack(
            side="left",
            padx=5
        )

        self.play_original_button = tk.Button(
            buttons,
            text="▶  Play Original",
            command=self.play_original,
            bg=self.card2,
            fg=self.text,
            activebackground="#303846",
            font=(
                "DejaVu Sans",
                10,
                "bold"
            ),
            relief="flat",
            padx=18,
            pady=12,
            cursor="hand2",
            state="disabled"
        )

        self.play_original_button.pack(
            side="left",
            padx=5
        )

        self.play_enhanced_button = tk.Button(
            buttons,
            text="▶  Play Enhanced",
            command=self.play_enhanced,
            bg=self.card2,
            fg=self.text,
            activebackground="#303846",
            font=(
                "DejaVu Sans",
                10,
                "bold"
            ),
            relief="flat",
            padx=18,
            pady=12,
            cursor="hand2",
            state="disabled"
        )

        self.play_enhanced_button.pack(
            side="left",
            padx=5
        )

        self.stop_audio_button = tk.Button(
            buttons,
            text="■  Stop Audio",
            command=self.stop_audio,
            bg=self.red,
            fg="#20070b",
            activebackground=self.red,
            font=(
                "DejaVu Sans",
                10,
                "bold"
            ),
            relief="flat",
            padx=18,
            pady=12,
            cursor="hand2"
        )

        self.stop_audio_button.pack(
            side="left",
            padx=5
        )

        # ----------------------------------------------------
        # RESULTS
        # ----------------------------------------------------

        results_card = tk.Frame(
            self.test_tab,
            bg=self.card2
        )

        results_card.pack(
            fill="x",
            padx=20,
            pady=10
        )

        self.test_metrics = tk.Label(
            results_card,
            text=(
                "TEST RESULTS\n\n"
                "No test completed yet."
            ),
            font=(
                "DejaVu Sans",
                10
            ),
            fg=self.text,
            bg=self.card2,
            justify="left"
        )

        self.test_metrics.pack(
            anchor="w",
            padx=20,
            pady=15
        )

    # ========================================================
    # MEETING MODE
    # ========================================================

    def build_meeting_mode(self):

        self.meeting_mic_combo = (
            self.create_microphone_card(
                self.meeting_tab
            )
        )

        level_card = tk.Frame(
            self.meeting_tab,
            bg=self.card,
            highlightbackground="#2a3039",
            highlightthickness=1
        )

        level_card.pack(
            fill="x",
            padx=20,
            pady=5
        )

        tk.Label(
            level_card,
            text="Live Audio Monitor",
            font=(
                "DejaVu Sans",
                13,
                "bold"
            ),
            fg=self.text,
            bg=self.card
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 12)
        )

        tk.Label(
            level_card,
            text="Microphone Input",
            font=(
                "DejaVu Sans",
                9
            ),
            fg=self.muted,
            bg=self.card
        ).pack(
            anchor="w",
            padx=20
        )

        self.input_meter = ttk.Progressbar(
            level_card,
            style="Horizontal.TProgressbar",
            maximum=1.0,
            mode="determinate"
        )

        self.input_meter.pack(
            fill="x",
            padx=20,
            pady=(5, 15)
        )

        tk.Label(
            level_card,
            text="Enhanced Output",
            font=(
                "DejaVu Sans",
                9
            ),
            fg=self.muted,
            bg=self.card
        ).pack(
            anchor="w",
            padx=20
        )

        self.output_meter = ttk.Progressbar(
            level_card,
            style="Horizontal.TProgressbar",
            maximum=1.0,
            mode="determinate"
        )

        self.output_meter.pack(
            fill="x",
            padx=20,
            pady=(5, 18)
        )

        # ----------------------------------------------------
        # CONTROLS
        # ----------------------------------------------------

        controls = tk.Frame(
            self.meeting_tab,
            bg=self.bg
        )

        controls.pack(
            fill="x",
            padx=20,
            pady=20
        )

        self.start_meeting_button = tk.Button(
            controls,
            text="▶  Start Meeting",
            command=self.start_meeting,
            bg=self.accent,
            fg="#071312",
            activebackground=self.accent,
            font=(
                "DejaVu Sans",
                12,
                "bold"
            ),
            relief="flat",
            padx=30,
            pady=14,
            cursor="hand2"
        )

        self.start_meeting_button.pack(
            side="left",
            padx=5
        )

        self.stop_meeting_button = tk.Button(
            controls,
            text="■  Stop Meeting",
            command=self.stop_meeting,
            bg=self.red,
            fg="#20070b",
            activebackground=self.red,
            font=(
                "DejaVu Sans",
                12,
                "bold"
            ),
            relief="flat",
            padx=30,
            pady=14,
            cursor="hand2",
            state="disabled"
        )

        self.stop_meeting_button.pack(
            side="left",
            padx=5
        )

        # ----------------------------------------------------
        # INFO
        # ----------------------------------------------------

        info = tk.Frame(
            self.meeting_tab,
            bg=self.card2
        )

        info.pack(
            fill="x",
            padx=20,
            pady=5
        )

        self.meeting_info = tk.Label(
            info,
            text=(
                "App Microphone: Ready\n"
                "Output: System Default Speaker / Headphones\n"
                "Processing: V4.1\n"
                "Recording: OFF\n"
                "Status: Ready"
            ),
            font=(
                "DejaVu Sans",
                10
            ),
            fg=self.text,
            bg=self.card2,
            justify="left"
        )

        self.meeting_info.pack(
            anchor="w",
            padx=20,
            pady=15
        )

    # ========================================================
    # DEVICE MANAGEMENT
    # ========================================================

    def refresh_devices(self):

        if sd is None:
            return

        try:

            devices = sd.query_devices()

            self.input_devices = []
            self.output_devices = []

            for index, device in enumerate(devices):

                if device["max_input_channels"] > 0:

                    self.input_devices.append(
                        (
                            index,
                            device["name"]
                        )
                    )

                if device["max_output_channels"] > 0:

                    self.output_devices.append(
                        (
                            index,
                            device["name"]
                        )
                    )

            input_names = [
                f"{name} [ID {index}]"
                for index, name
                in self.input_devices
            ]

            output_names = [
                f"{name} [ID {index}]"
                for index, name
                in self.output_devices
            ]

            self.test_mic_combo["values"] = (
                input_names
            )

            self.meeting_mic_combo["values"] = (
                input_names
            )

            self.test_output_combo["values"] = (
                output_names
            )

            default_input, default_output = (
                sd.default.device
            )

            input_position = 0

            for position, (
                index,
                _
            ) in enumerate(self.input_devices):

                if index == default_input:

                    input_position = position
                    break

            output_position = 0

            for position, (
                index,
                _
            ) in enumerate(self.output_devices):

                if index == default_output:

                    output_position = position
                    break

            if input_names:

                self.test_mic_combo.current(
                    input_position
                )

                self.meeting_mic_combo.current(
                    input_position
                )

            if output_names:

                self.test_output_combo.current(
                    output_position
                )

        except Exception as error:

            messagebox.showerror(
                "Audio Device Error",
                str(error)
            )

    # ========================================================
    # GET INPUT
    # ========================================================

    def get_selected_input(self, combo):

        position = combo.current()

        if position < 0:

            raise RuntimeError(
                "Please select an App Microphone."
            )

        return self.input_devices[position][0]

    # ========================================================
    # GET OUTPUT
    # ========================================================

    def get_selected_output(self):

        position = (
            self.test_output_combo.current()
        )

        if position < 0:

            raise RuntimeError(
                "Please select a speaker/headphone."
            )

        return self.output_devices[position][0]

    # ========================================================
    # START TEST
    # ========================================================

    def start_test(self):

        if self.test_recording:
            return

        try:

            input_device = (
                self.get_selected_input(
                    self.test_mic_combo
                )
            )

        except Exception as error:

            messagebox.showerror(
                "Microphone Error",
                str(error)
            )

            return

        self.test_recording = True
        self.test_cancel = False

        self.record_button.config(
            state="disabled"
        )

        self.cancel_test_button.config(
            state="normal"
        )

        self.play_original_button.config(
            state="disabled"
        )

        self.play_enhanced_button.config(
            state="disabled"
        )

        self.set_status(
            "RECORDING",
            self.blue
        )

        self.test_timer_label.config(
            text="Recording: 30 seconds remaining"
        )

        thread = threading.Thread(
            target=self.record_test_worker,
            args=(input_device,),
            daemon=True
        )

        thread.start()

    # ========================================================
    # RECORD TEST
    # ========================================================

    def record_test_worker(self, input_device):

        try:

            total_frames = int(
                TEST_DURATION * SAMPLE_RATE
            )

            chunks = []
            frames_recorded = 0

            def callback(
                indata,
                frames,
                time_info,
                status
            ):

                nonlocal frames_recorded

                if self.test_cancel:
                    raise sd.CallbackStop()

                remaining = (
                    total_frames -
                    frames_recorded
                )

                take = min(
                    frames,
                    remaining
                )

                if take > 0:

                    chunks.append(
                        indata[:take, 0].copy()
                    )

                    frames_recorded += take

                if frames_recorded >= total_frames:

                    raise sd.CallbackStop()

            stream = sd.InputStream(
                samplerate=SAMPLE_RATE,
                blocksize=BLOCK_SIZE,
                channels=CHANNELS,
                dtype="float32",
                device=input_device,
                callback=callback,
                latency="low"
            )

            start_time = time.perf_counter()

            with stream:

                while (
                    frames_recorded < total_frames
                    and
                    not self.test_cancel
                ):

                    elapsed = (
                        time.perf_counter()
                        - start_time
                    )

                    remaining = max(
                        0,
                        TEST_DURATION -
                        int(elapsed)
                    )

                    self.root.after(
                        0,
                        lambda r=remaining:
                        self.update_record_timer(r)
                    )

                    time.sleep(0.05)

            if self.test_cancel:

                self.root.after(
                    0,
                    self.test_cancelled
                )

                return

            if not chunks:

                raise RuntimeError(
                    "No audio was captured."
                )

            audio = np.concatenate(chunks)

            audio = audio[:total_frames]

            if len(audio) < total_frames:

                audio = np.pad(
                    audio,
                    (
                        0,
                        total_frames - len(audio)
                    )
                )

            self.root.after(
                0,
                lambda:
                self.test_timer_label.config(
                    text=(
                        "✓ Recording completed\n"
                        "Applying V4.1 enhancement..."
                    )
                )
            )

            # ------------------------------------------------
            # SAVE ORIGINAL
            # ------------------------------------------------

            original_path = (
                INPUT_DIR /
                "test_original_v41.wav"
            )

            sf.write(
                str(original_path),
                audio,
                SAMPLE_RATE,
                subtype="PCM_16"
            )

            # ------------------------------------------------
            # V4.1 PROCESSOR
            # ------------------------------------------------

            reducer = SpectralNoiseReducer(
                sample_rate=SAMPLE_RATE,
                frame_size=2048,
                hop_size=512,
                noise_search_duration=10.0,
                noise_update_rate=0.03,
                reduction_strength=0.55,
                minimum_gain=0.55,
                smoothing=0.85
            )

            start_processing = time.perf_counter()

            enhanced = reducer.process(audio)

            processing_time = (
                time.perf_counter()
                - start_processing
            )

            enhanced = np.asarray(
                enhanced,
                dtype=np.float32
            ).reshape(-1)

            # ------------------------------------------------
            # MATCH LENGTH
            # ------------------------------------------------

            if len(enhanced) < len(audio):

                enhanced = np.pad(
                    enhanced,
                    (
                        0,
                        len(audio) - len(enhanced)
                    )
                )

            elif len(enhanced) > len(audio):

                enhanced = enhanced[:len(audio)]

            # ------------------------------------------------
            # OUTPUT GAIN
            # ------------------------------------------------

            enhanced = enhanced * OUTPUT_GAIN

            # ------------------------------------------------
            # CLIPPING PROTECTION
            # ------------------------------------------------

            enhanced = np.clip(
                enhanced,
                -1.0,
                1.0
            )

            # ------------------------------------------------
            # SAVE ENHANCED
            # ------------------------------------------------

            enhanced_path = (
                OUTPUT_DIR /
                "test_enhanced_v41.wav"
            )

            sf.write(
                str(enhanced_path),
                enhanced,
                SAMPLE_RATE,
                subtype="PCM_16"
            )

            # ------------------------------------------------
            # STORE
            # ------------------------------------------------

            self.test_original = audio
            self.test_enhanced = enhanced

            # ------------------------------------------------
            # GENERATE PLOTS
            # ------------------------------------------------

            self.root.after(
                0,
                lambda:
                self.test_timer_label.config(
                    text="Generating comparison plots..."
                )
            )

            create_waveform_plot(
                audio,
                enhanced,
                SAMPLE_RATE
            )

            create_spectrogram_plot(
                audio,
                enhanced,
                SAMPLE_RATE
            )

            create_metrics_plot(
                audio,
                enhanced
            )

            # ------------------------------------------------
            # METRICS
            # ------------------------------------------------

            original_rms = float(
                np.sqrt(
                    np.mean(audio ** 2)
                )
            )

            enhanced_rms = float(
                np.sqrt(
                    np.mean(enhanced ** 2)
                )
            )

            original_peak = float(
                np.max(
                    np.abs(audio)
                )
            )

            enhanced_peak = float(
                np.max(
                    np.abs(enhanced)
                )
            )

            rms_change = (
                20 *
                np.log10(
                    enhanced_rms /
                    max(
                        original_rms,
                        1e-10
                    )
                )
            )

            self.root.after(
                0,
                lambda:
                self.test_complete(
                    original_rms,
                    enhanced_rms,
                    original_peak,
                    enhanced_peak,
                    rms_change,
                    processing_time
                )
            )

        except Exception as error:

            self.root.after(
                0,
                lambda:
                self.test_failed(str(error))
            )

    # ========================================================
    # TIMER
    # ========================================================

    def update_record_timer(self, remaining):

        if not self.test_recording:
            return

        if remaining > 0:

            self.test_timer_label.config(
                text=(
                    f"Recording: "
                    f"{remaining} "
                    f"seconds remaining"
                )
            )

        else:

            self.test_timer_label.config(
                text="Finishing recording..."
            )

    # ========================================================
    # CANCEL TEST
    # ========================================================

    def cancel_test(self):

        if not self.test_recording:
            return

        self.test_cancel = True

        self.set_status(
            "CANCELLING TEST",
            self.orange
        )

        self.test_timer_label.config(
            text="Stopping recording..."
        )

    # ========================================================
    # CANCELLED
    # ========================================================

    def test_cancelled(self):

        self.test_recording = False

        self.record_button.config(
            state="normal"
        )

        self.cancel_test_button.config(
            state="disabled"
        )

        self.set_status(
            "READY",
            self.green
        )

        self.test_timer_label.config(
            text="Test cancelled"
        )

    # ========================================================
    # TEST COMPLETE
    # ========================================================

    def test_complete(
        self,
        original_rms,
        enhanced_rms,
        original_peak,
        enhanced_peak,
        rms_change,
        processing_time
    ):

        self.test_recording = False

        self.record_button.config(
            state="normal"
        )

        self.cancel_test_button.config(
            state="disabled"
        )

        self.play_original_button.config(
            state="normal"
        )

        self.play_enhanced_button.config(
            state="normal"
        )

        self.test_timer_label.config(
            text="✓ 30-second test completed"
        )

        self.set_status(
            "TEST COMPLETE",
            self.green
        )

        self.test_metrics.config(
            text=(
                "V4.1 TEST RESULTS\n\n"

                f"Original RMS   : "
                f"{original_rms:.6f}\n"

                f"Enhanced RMS   : "
                f"{enhanced_rms:.6f}\n\n"

                f"Original Peak  : "
                f"{original_peak:.6f}\n"

                f"Enhanced Peak  : "
                f"{enhanced_peak:.6f}\n\n"

                f"RMS Change     : "
                f"{rms_change:+.2f} dB\n"

                f"Output Gain    : "
                f"{OUTPUT_GAIN:.1f}x\n"

                f"Processing Time: "
                f"{processing_time:.3f} sec\n\n"

                "INPUT AUDIO\n"
                "input/test_original_v41.wav\n\n"

                "ENHANCED AUDIO\n"
                "output/test_enhanced_v41.wav\n\n"

                "COMPARISON PLOTS\n"
                "plots/waveform_comparison.png\n"
                "plots/spectrogram_comparison.png\n"
                "plots/audio_metrics.png"
            )
        )

    # ========================================================
    # TEST FAILED
    # ========================================================

    def test_failed(self, error):

        self.test_recording = False

        self.record_button.config(
            state="normal"
        )

        self.cancel_test_button.config(
            state="disabled"
        )

        self.play_original_button.config(
            state="disabled"
        )

        self.play_enhanced_button.config(
            state="disabled"
        )

        self.set_status(
            "ERROR",
            self.red
        )

        self.test_timer_label.config(
            text="Test failed"
        )

        messagebox.showerror(
            "Test Mode Error",
            error
        )

    # ========================================================
    # PLAY ORIGINAL
    # ========================================================

    def play_original(self):

        path = (
            INPUT_DIR /
            "test_original_v41.wav"
        )

        self.play_file(
            path,
            "ORIGINAL AUDIO"
        )

    # ========================================================
    # PLAY ENHANCED
    # ========================================================

    def play_enhanced(self):

        path = (
            OUTPUT_DIR /
            "test_enhanced_v41.wav"
        )

        self.play_file(
            path,
            "ENHANCED AUDIO"
        )

    # ========================================================
    # PLAY FILE
    # ========================================================

    def play_file(
        self,
        path,
        title
    ):

        if not path.exists():

            messagebox.showwarning(
                "Audio Not Found",
                f"File not found:\n{path}"
            )

            return

        try:

            output_device = (
                self.get_selected_output()
            )

        except Exception as error:

            messagebox.showerror(
                "Output Error",
                str(error)
            )

            return

        self.stop_audio()

        threading.Thread(
            target=self.play_file_worker,
            args=(
                path,
                output_device,
                title
            ),
            daemon=True
        ).start()

    # ========================================================
    # PLAY WORKER
    # ========================================================

    def play_file_worker(
        self,
        path,
        output_device,
        title
    ):

        try:

            self.playing = True

            self.root.after(
                0,
                lambda:
                self.set_status(
                    f"PLAYING {title}",
                    self.blue
                )
            )

            audio, samplerate = sf.read(
                str(path),
                dtype="float32"
            )

            if audio.ndim > 1:

                audio = np.mean(
                    audio,
                    axis=1
                )

            audio = np.asarray(
                audio,
                dtype=np.float32
            )

            sd.play(
                audio,
                samplerate,
                device=output_device,
                blocking=True
            )

        except Exception as error:

            self.root.after(
                0,
                lambda:
                messagebox.showerror(
                    "Playback Error",
                    str(error)
                )
            )

        finally:

            self.playing = False

            self.root.after(
                0,
                lambda:
                self.set_status(
                    "READY",
                    self.green
                )
            )

    # ========================================================
    # STOP AUDIO
    # ========================================================

    def stop_audio(self):

        try:
            sd.stop()
        except Exception:
            pass

        self.playing = False

        self.set_status(
            "READY",
            self.green
        )

    # ========================================================
    # MEETING MODE
    # ========================================================

    def start_meeting(self):

        if self.meeting_running:
            return

        try:

            input_device = (
                self.get_selected_input(
                    self.meeting_mic_combo
                )
            )

        except Exception as error:

            messagebox.showerror(
                "Microphone Error",
                str(error)
            )

            return

        self.meeting_running = True
        self.meeting_cancel = False

        self.start_meeting_button.config(
            state="disabled"
        )

        self.stop_meeting_button.config(
            state="normal"
        )

        self.set_status(
            "STARTING",
            self.blue
        )

        self.meeting_info.config(
            text=(
                "App Microphone: Active\n"
                "Output: System Default Speaker / Headphones\n"
                "Processing: V4.1\n"
                "Status: Starting live enhancement..."
            )
        )

        self.meeting_thread = threading.Thread(
            target=self.meeting_worker,
            args=(input_device,),
            daemon=True
        )

        self.meeting_thread.start()

    # ========================================================
    # MEETING WORKER
    # ========================================================

    def meeting_worker(self, input_device):

        try:

            self.live_reducer = SpectralNoiseReducer(
                sample_rate=SAMPLE_RATE,
                frame_size=BLOCK_SIZE,
                hop_size=512,
                noise_search_duration=10.0,
                noise_update_rate=0.03,
                reduction_strength=0.55,
                minimum_gain=0.55,
                smoothing=0.85
            )

            self.start_meeting_stream(
                input_device
            )

        except Exception as error:

            self.root.after(
                0,
                lambda:
                self.meeting_failed(str(error))
            )

    # ========================================================
    # LIVE STREAM
    # ========================================================

    def start_meeting_stream(self, input_device):

        _, default_output = sd.default.device

        def callback(
            indata,
            outdata,
            frames,
            time_info,
            status
        ):

            start_time = time.perf_counter()

            incoming = indata[:, 0].copy()

            self.input_level = float(
                np.sqrt(
                    np.mean(
                        incoming ** 2
                    )
                )
            )

            try:

                enhanced = (
                    self.live_reducer.process(
                        incoming
                    )
                )

                enhanced = np.asarray(
                    enhanced,
                    dtype=np.float32
                ).reshape(-1)

                if len(enhanced) < frames:

                    enhanced = np.pad(
                        enhanced,
                        (
                            0,
                            frames - len(enhanced)
                        )
                    )

                elif len(enhanced) > frames:

                    enhanced = enhanced[:frames]

                # ------------------------------------------------
                # LIVE OUTPUT GAIN
                # ------------------------------------------------

                enhanced = (
                    enhanced *
                    OUTPUT_GAIN
                )

                enhanced = np.clip(
                    enhanced,
                    -1.0,
                    1.0
                )

                outdata[:, 0] = enhanced

                self.output_level = float(
                    np.sqrt(
                        np.mean(
                            enhanced ** 2
                        )
                    )
                )

            except Exception:

                outdata[:, 0] = incoming

                self.output_level = (
                    self.input_level
                )

            self.processing_ms = (
                time.perf_counter()
                - start_time
            ) * 1000.0

        self.meeting_stream = sd.Stream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            channels=1,
            dtype="float32",
            device=(
                input_device,
                default_output
            ),
            callback=callback,
            latency="low"
        )

        self.meeting_stream.start()

        self.root.after(
            0,
            self.meeting_started
        )

    # ========================================================
    # MEETING STARTED
    # ========================================================

    def meeting_started(self):

        self.set_status(
            "MEETING ACTIVE",
            self.green
        )

        self.meeting_info.config(
            text=(
                "App Microphone: ACTIVE\n"
                "Output: System Default Speaker / Headphones\n"
                "Processing: V4.1\n"
                "Recording: OFF\n"
                "Status: LIVE"
            )
        )

    # ========================================================
    # STOP MEETING
    # ========================================================

    def stop_meeting(self):

        self.meeting_cancel = True
        self.meeting_running = False

        try:

            if self.meeting_stream is not None:

                self.meeting_stream.stop()
                self.meeting_stream.close()

        except Exception:
            pass

        self.meeting_stream = None

        try:
            sd.stop()
        except Exception:
            pass

        self.input_level = 0.0
        self.output_level = 0.0

        self.start_meeting_button.config(
            state="normal"
        )

        self.stop_meeting_button.config(
            state="disabled"
        )

        self.set_status(
            "READY",
            self.green
        )

        self.meeting_info.config(
            text=(
                "App Microphone: Ready\n"
                "Output: System Default Speaker / Headphones\n"
                "Processing: V4.1\n"
                "Recording: OFF\n"
                "Status: Ready"
            )
        )

    # ========================================================
    # MEETING FAILED
    # ========================================================

    def meeting_failed(self, error):

        self.meeting_running = False

        try:

            if self.meeting_stream is not None:

                self.meeting_stream.stop()
                self.meeting_stream.close()

        except Exception:
            pass

        self.meeting_stream = None

        self.start_meeting_button.config(
            state="normal"
        )

        self.stop_meeting_button.config(
            state="disabled"
        )

        self.set_status(
            "ERROR",
            self.red
        )

        messagebox.showerror(
            "Meeting Mode Error",
            error
        )

    # ========================================================
    # METERS
    # ========================================================

    def update_meters(self):

        input_value = min(
            1.0,
            self.input_level * 8.0
        )

        output_value = min(
            1.0,
            self.output_level * 8.0
        )

        self.input_meter["value"] = (
            input_value
        )

        self.output_meter["value"] = (
            output_value
        )

        if self.meeting_running:

            self.meeting_info.config(
                text=(
                    "App Microphone: ACTIVE\n"
                    "Output: System Default Speaker / Headphones\n"
                    "Processing: V4.1\n"
                    "Recording: OFF\n"
                    "Status: LIVE\n"
                    f"Processing block: "
                    f"{self.processing_ms:.2f} ms"
                )
            )

        self.root.after(
            100,
            self.update_meters
        )

    # ========================================================
    # STATUS
    # ========================================================

    def set_status(
        self,
        text,
        color
    ):

        self.status_label.config(
            text=f"●  {text}",
            fg=color
        )

    # ========================================================
    # CLOSE
    # ========================================================

    def close_app(self):

        self.test_cancel = True
        self.meeting_cancel = True

        self.test_recording = False
        self.meeting_running = False

        try:
            sd.stop()
        except Exception:
            pass

        try:

            if self.meeting_stream is not None:

                self.meeting_stream.stop()
                self.meeting_stream.close()

        except Exception:
            pass

        self.root.destroy()


# ============================================================
# MAIN
# ============================================================

def main():

    if sd is None:

        root = tk.Tk()
        root.withdraw()

        messagebox.showerror(
            "Missing Dependency",
            "The sounddevice package is required.\n\n"
            "Install it with:\n"
            "python -m pip install sounddevice\n\n"
            f"Details: {_sounddevice_import_error}"
        )

        root.destroy()
        return

    root = tk.Tk()

    app = SpeechEnhancementApp(
        root
    )

    root.mainloop()


if __name__ == "__main__":
    main()
