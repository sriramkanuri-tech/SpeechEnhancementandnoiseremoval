import os
import time

import numpy as np
import sounddevice as sd
import soundfile as sf

from spectral_noise_reduction import SpectralNoiseReducer


# ============================================================
# PHASE 2 - STEP 3
# SINGLE-CHANNEL SPECTRAL NOISE REDUCTION TEST
# ============================================================

SAMPLE_RATE = 48000
CHANNELS = 1
DURATION = 30

OUTPUT_DIR = "../output"

ORIGINAL_FILE = os.path.join(
    OUTPUT_DIR,
    "test_original.wav"
)

ENHANCED_FILE = os.path.join(
    OUTPUT_DIR,
    "test_enhanced.wav"
)


def record_audio():

    print("\n" + "=" * 60)
    print("30-SECOND SPEECH RECORDING")
    print("=" * 60)

    print("\nMicrophone : Default System Microphone")
    print(f"Sample rate: {SAMPLE_RATE} Hz")
    print(f"Duration   : {DURATION} seconds")

    print("\nIMPORTANT:")
    print("Remain SILENT for the first 3 seconds.")
    print("This period is used to estimate background noise.")
    print("After that, speak normally.")

    print("\nRecording starts in 3 seconds...")

    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)

    print("\n🎙️ RECORDING...")

    try:

        audio = sd.rec(
            int(DURATION * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="float32"
        )

        sd.wait()

        audio = audio.reshape(-1)

        sf.write(
            ORIGINAL_FILE,
            audio,
            SAMPLE_RATE,
            subtype="PCM_16"
        )

        print("\n✓ Recording completed")
        print(f"✓ Original saved: {ORIGINAL_FILE}")

        return audio

    except Exception as e:

        print("\nRecording error:")
        print(e)

        return None


def enhance_audio(audio):

    print("\n" + "=" * 60)
    print("SPECTRAL NOISE REDUCTION")
    print("=" * 60)

    print("Noise estimation duration: 3 seconds")
    print("Processing audio using FFT-based spectral reduction...")

    try:

        reducer = SpectralNoiseReducer(
            sample_rate=SAMPLE_RATE,
            frame_size=2048,
            hop_size=512,
            noise_duration=3.0,
            reduction_strength=1.5,
            minimum_gain=0.12
        )

        start_time = time.perf_counter()

        enhanced = reducer.process(
            audio
        )

        processing_time = (
            time.perf_counter()
            - start_time
        )

        sf.write(
            ENHANCED_FILE,
            enhanced,
            SAMPLE_RATE,
            subtype="PCM_16"
        )

        print("✓ Noise reduction completed")
        print(f"✓ Enhanced saved: {ENHANCED_FILE}")
        print(
            f"✓ Processing time: "
            f"{processing_time:.3f} seconds"
        )

        return enhanced, processing_time

    except Exception as e:

        print("\nEnhancement error:")
        print(e)

        return None, None


def calculate_metrics(original, enhanced):

    print("\n" + "=" * 60)
    print("AUDIO ANALYSIS")
    print("=" * 60)

    original_rms = np.sqrt(
        np.mean(original ** 2)
    )

    enhanced_rms = np.sqrt(
        np.mean(enhanced ** 2)
    )

    original_peak = np.max(
        np.abs(original)
    )

    enhanced_peak = np.max(
        np.abs(enhanced)
    )

    print(
        f"Original RMS  : "
        f"{original_rms:.6f}"
    )

    print(
        f"Enhanced RMS  : "
        f"{enhanced_rms:.6f}"
    )

    print(
        f"Original peak : "
        f"{original_peak:.6f}"
    )

    print(
        f"Enhanced peak : "
        f"{enhanced_peak:.6f}"
    )

    if original_rms > 0:

        rms_change_db = 20 * np.log10(
            enhanced_rms / original_rms
        )

        print(
            f"RMS change    : "
            f"{rms_change_db:+.2f} dB"
        )


def play_audio(audio, name):

    print(f"\n🔊 Playing {name}...")
    print(
        "Output: Default system speaker/headphones"
    )

    try:

        sd.play(
            audio,
            SAMPLE_RATE
        )

        sd.wait()

        print("✓ Playback completed")

    except Exception as e:

        print("\nPlayback error:")
        print(e)


def main():

    print("\n")
    print("=" * 60)
    print(" SPEECH ENHANCEMENT AND NOISE REMOVAL")
    print(" PHASE 2 - TEST MODE")
    print("=" * 60)

    original = record_audio()

    if original is None:
        return

    enhanced, processing_time = enhance_audio(
        original
    )

    if enhanced is None:
        return

    calculate_metrics(
        original,
        enhanced
    )

    print("\n" + "=" * 60)
    print("AUDIO COMPARISON")
    print("=" * 60)

    input(
        "\nPress ENTER to play ORIGINAL audio..."
    )

    play_audio(
        original,
        "ORIGINAL AUDIO"
    )

    input(
        "\nPress ENTER to play ENHANCED audio..."
    )

    play_audio(
        enhanced,
        "ENHANCED AUDIO"
    )

    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)

    print("\nFiles created:")
    print(f"Original : {ORIGINAL_FILE}")
    print(f"Enhanced : {ENHANCED_FILE}")

    if processing_time is not None:

        print(
            f"\nProcessing time for "
            f"30-second audio: "
            f"{processing_time:.3f} seconds"
        )


if __name__ == "__main__":
    main()
