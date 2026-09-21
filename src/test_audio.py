import sounddevice as sd
import soundfile as sf
import numpy as np
import os
import time

# ==============================
# Phase 2 - Audio Test
# ==============================

SAMPLE_RATE = 48000
CHANNELS = 1
DURATION = 30

OUTPUT_DIR = "output"
ORIGINAL_FILE = os.path.join(OUTPUT_DIR, "test_original.wav")

os.makedirs(OUTPUT_DIR, exist_ok=True)


def record_audio():
    print("=" * 60)
    print("SPEECH ENHANCEMENT - MICROPHONE TEST")
    print("=" * 60)

    print("\nUsing the DEFAULT system microphone.")
    print(f"Sample rate : {SAMPLE_RATE} Hz")
    print(f"Channels    : {CHANNELS}")
    print(f"Duration    : {DURATION} seconds")

    print("\nRecording will start in 3 seconds...")

    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)

    print("\n🎙️ RECORDING STARTED")
    print("Speak normally into your microphone.")
    print("You can also create some background noise for testing.\n")

    try:
        audio = sd.rec(
            int(DURATION * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="float32",
            device=None
        )

        # Wait until recording is completely finished
        sd.wait()

        print("\nRecording completed.")

        # Remove any extra dimensions
        audio = np.asarray(audio).reshape(-1)

        # Save original recording
        sf.write(
            ORIGINAL_FILE,
            audio,
            SAMPLE_RATE,
            subtype="PCM_16"
        )

        print(f"Saved: {ORIGINAL_FILE}")

        return audio

    except Exception as e:
        print("\nERROR while recording:")
        print(e)
        return None


def play_audio(audio):
    print("\n🔊 Playing recording through the DEFAULT system output...")
    print("Please listen carefully.\n")

    try:
        sd.play(
            audio,
            SAMPLE_RATE,
            device=None
        )

        sd.wait()

        print("Playback completed.")

    except Exception as e:
        print("\nERROR during playback:")
        print(e)


def main():
    audio = record_audio()

    if audio is None:
        return

    print("\n" + "=" * 60)
    print("RECORDING TEST RESULT")
    print("=" * 60)

    print(f"Number of samples : {len(audio)}")
    print(f"Duration          : {len(audio) / SAMPLE_RATE:.2f} seconds")
    print(f"Maximum amplitude : {np.max(np.abs(audio)):.4f}")
    print(f"RMS level         : {np.sqrt(np.mean(audio ** 2)):.4f}")

    input("\nPress ENTER to play the recorded audio...")

    play_audio(audio)

    print("\nTest completed successfully.")


if __name__ == "__main__":
    main()
