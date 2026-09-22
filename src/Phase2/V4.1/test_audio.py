import sounddevice as sd
import soundfile as sf
import numpy as np
import time
from pathlib import Path

# ============================================================
# Phase 2 - Audio Recording Test
# ============================================================

SAMPLE_RATE = 48000
CHANNELS = 1
DURATION = 30

# ------------------------------------------------------------
# Project paths
# test_audio.py is inside:
# src/Phase2/V4.1/
#
# parents[0] = V4.1
# parents[1] = Phase2
# ------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_DIR = PROJECT_ROOT / "input"
INPUT_DIR.mkdir(parents=True, exist_ok=True)

ORIGINAL_FILE = INPUT_DIR / "test_original_v41.wav"


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

        # Convert to one-dimensional array
        audio = np.asarray(audio).reshape(-1)

        # Save directly to Phase2/input/
        sf.write(
            str(ORIGINAL_FILE),
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