import tkinter as tk
from tkinter import ttk
import sounddevice as sd


class SpeechEnhancementApp:
    def __init__(self, root):
        self.root = root

        # ---------------------------------------------------------
        # Window
        # ---------------------------------------------------------
        self.root.title("Speech Enhancement and Noise Removal")
        self.root.geometry("750x500")
        self.root.resizable(False, False)

        # ---------------------------------------------------------
        # Title
        # ---------------------------------------------------------
        title = tk.Label(
            self.root,
            text="Speech Enhancement and Noise Removal",
            font=("Arial", 20, "bold")
        )
        title.pack(pady=(25, 5))

        subtitle = tk.Label(
            self.root,
            text="Phase 2 - V4.1",
            font=("Arial", 13)
        )
        subtitle.pack(pady=(0, 20))

        # ---------------------------------------------------------
        # Device Frame
        # ---------------------------------------------------------
        device_frame = ttk.LabelFrame(
            self.root,
            text="Audio Devices"
        )
        device_frame.pack(
            fill="x",
            padx=30,
            pady=10
        )

        # ---------------------------------------------------------
        # Microphone
        # ---------------------------------------------------------
        microphone_label = ttk.Label(
            device_frame,
            text="App Microphone:"
        )
        microphone_label.grid(
            row=0,
            column=0,
            padx=15,
            pady=20,
            sticky="w"
        )

        self.microphone_combo = ttk.Combobox(
            device_frame,
            state="readonly",
            width=55
        )
        self.microphone_combo.grid(
            row=0,
            column=1,
            padx=15,
            pady=20
        )

        # ---------------------------------------------------------
        # Output
        # ---------------------------------------------------------
        output_label = ttk.Label(
            device_frame,
            text="Test Output:"
        )
        output_label.grid(
            row=1,
            column=0,
            padx=15,
            pady=20,
            sticky="w"
        )

        self.output_combo = ttk.Combobox(
            device_frame,
            state="readonly",
            width=55
        )
        self.output_combo.grid(
            row=1,
            column=1,
            padx=15,
            pady=20
        )

        # ---------------------------------------------------------
        # Device Detection Button
        # ---------------------------------------------------------
        self.detect_button = ttk.Button(
            self.root,
            text="Test Device Detection",
            command=self.test_devices
        )
        self.detect_button.pack(pady=25)

        # ---------------------------------------------------------
        # Status
        # ---------------------------------------------------------
        self.status_label = tk.Label(
            self.root,
            text="Ready",
            font=("Arial", 11)
        )
        self.status_label.pack(pady=10)

        # ---------------------------------------------------------
        # Default device information
        # ---------------------------------------------------------
        self.default_label = tk.Label(
            self.root,
            text="Default device: checking...",
            font=("Arial", 10)
        )
        self.default_label.pack(pady=5)

        # ---------------------------------------------------------
        # Initial device detection
        # ---------------------------------------------------------
        self.root.after(100, self.test_devices)

    # =============================================================
    # DEVICE DETECTION
    # =============================================================
    def test_devices(self):

        try:
            print()
            print("=" * 60)
            print("DEVICE DETECTION")
            print("=" * 60)

            self.status_label.config(
                text="Detecting audio devices..."
            )

            # -----------------------------------------------------
            # Get default device
            # -----------------------------------------------------
            default_device = sd.default.device

            print("Default device:", default_device)

            self.default_label.config(
                text=f"Default device: Input {default_device[0]} / "
                     f"Output {default_device[1]}"
            )

            # -----------------------------------------------------
            # Query devices
            # -----------------------------------------------------
            print("Querying devices...")

            devices = sd.query_devices()

            print("Device query successful.")
            print()

            input_devices = []
            output_devices = []

            # -----------------------------------------------------
            # Process device list
            # -----------------------------------------------------
            for index, device in enumerate(devices):

                name = device["name"]
                max_inputs = device["max_input_channels"]
                max_outputs = device["max_output_channels"]

                print(
                    f"{index}: {name} "
                    f"(inputs={max_inputs}, outputs={max_outputs})"
                )

                # -------------------------------------------------
                # Input device
                # -------------------------------------------------
                if max_inputs > 0:

                    input_devices.append(
                        f"{index}: {name}"
                    )

                # -------------------------------------------------
                # Output device
                # -------------------------------------------------
                if max_outputs > 0:

                    output_devices.append(
                        f"{index}: {name}"
                    )

            # -----------------------------------------------------
            # Put devices into microphone combobox
            # -----------------------------------------------------
            self.microphone_combo["values"] = input_devices

            # -----------------------------------------------------
            # Put devices into output combobox
            # -----------------------------------------------------
            self.output_combo["values"] = output_devices

            # -----------------------------------------------------
            # Select default microphone
            # -----------------------------------------------------
            default_input = default_device[0]

            if default_input is not None and default_input >= 0:

                for position, item in enumerate(input_devices):

                    if item.startswith(f"{default_input}:"):

                        self.microphone_combo.current(position)
                        break

            # -----------------------------------------------------
            # Select default output
            # -----------------------------------------------------
            default_output = default_device[1]

            if default_output is not None and default_output >= 0:

                for position, item in enumerate(output_devices):

                    if item.startswith(f"{default_output}:"):

                        self.output_combo.current(position)
                        break

            # -----------------------------------------------------
            # If no default was selected, select first device
            # -----------------------------------------------------
            if input_devices and self.microphone_combo.current() == -1:

                self.microphone_combo.current(0)

            if output_devices and self.output_combo.current() == -1:

                self.output_combo.current(0)

            # -----------------------------------------------------
            # Success
            # -----------------------------------------------------
            self.status_label.config(
                text=(
                    f"Device detection successful: "
                    f"{len(input_devices)} input device(s), "
                    f"{len(output_devices)} output device(s)"
                )
            )

            print()
            print("Input devices:", len(input_devices))
            print("Output devices:", len(output_devices))
            print("Device detection completed.")
            print("=" * 60)

        except Exception as error:

            print()
            print("=" * 60)
            print("DEVICE DETECTION ERROR")
            print("=" * 60)
            print(repr(error))
            print("=" * 60)

            self.status_label.config(
                text=f"Device detection error: {error}"
            )


# ================================================================
# MAIN
# ================================================================
def main():

    print()
    print("=" * 60)
    print("SPEECH ENHANCEMENT AND NOISE REMOVAL")
    print("PHASE 2 - V4.1")
    print("=" * 60)

    try:

        # ---------------------------------------------------------
        # Create Tkinter window
        # ---------------------------------------------------------
        print("Creating Tkinter window...")

        root = tk.Tk()

        print("Tkinter window created.")

        # ---------------------------------------------------------
        # Create application
        # ---------------------------------------------------------
        print("Initializing application...")

        app = SpeechEnhancementApp(root)

        print("Application initialized.")

        print("Starting GUI...")
        print("=" * 60)
        print()

        # ---------------------------------------------------------
        # Start GUI event loop
        # ---------------------------------------------------------
        root.mainloop()

    except Exception as error:

        print()
        print("=" * 60)
        print("APPLICATION ERROR")
        print("=" * 60)
        print(repr(error))
        print("=" * 60)

        raise


# ================================================================
# PROGRAM ENTRY POINT
# ================================================================
if __name__ == "__main__":
    main()
