import os
import time

import numpy as np
import soundfile as sf

from spectral_noise_reduction import SpectralNoiseReducer


INPUT_FILE = "../output/test_original.wav"
OUTPUT_FILE = "../output/test_enhanced_v3.wav"


def main():
    print("\n" + "=" * 60)
    print("PHASE 2 - WIENER-STYLE SPEECH ENHANCEMENT TEST")
    print("=" * 60)

    print(f"\nInput : {INPUT_FILE}")
    print(f"Output: {OUTPUT_FILE}")

    if not os.path.exists(INPUT_FILE):
        print("\nERROR: Original recording was not found.")
        return

    audio, sample_rate = sf.read(INPUT_FILE)

    if audio.ndim > 1:
        audio = audio.mean(axis=1)

    audio = audio.astype(np.float32)

    print(f"\nSample rate: {sample_rate} Hz")
    print(f"Duration   : {len(audio) / sample_rate:.2f} seconds")

    reducer = SpectralNoiseReducer(
        sample_rate=sample_rate,
        frame_size=2048,
        hop_size=512,
        noise_duration=3.0,
        reduction_strength=0.55,
        minimum_gain=0.55,
    )

    print("\nProcessing...")
    start = time.perf_counter()

    enhanced = reducer.process(audio)

    processing_time = time.perf_counter() - start

    sf.write(
        OUTPUT_FILE,
        enhanced,
        sample_rate,
        subtype="PCM_16",
    )

    original_rms = float(np.sqrt(np.mean(audio ** 2)))
    enhanced_rms = float(np.sqrt(np.mean(enhanced ** 2)))
    original_peak = float(np.max(np.abs(audio)))
    enhanced_peak = float(np.max(np.abs(enhanced)))

    print("\n✓ Processing completed")
    print(f"✓ Processing time: {processing_time:.3f} seconds")
    print(f"✓ Created: {OUTPUT_FILE}")

    print("\n" + "=" * 60)
    print("AUDIO METRICS")
    print("=" * 60)

    print(f"Original RMS : {original_rms:.6f}")
    print(f"Enhanced RMS : {enhanced_rms:.6f}")
    print(f"Original peak: {original_peak:.6f}")
    print(f"Enhanced peak: {enhanced_peak:.6f}")

    if original_rms > 0:
        rms_change_db = 20 * np.log10(
            max(enhanced_rms, 1e-12) / original_rms
        )
        print(f"RMS change   : {rms_change_db:+.2f} dB")

    print("\nNext command:")
    print(f"  pw-play {OUTPUT_FILE}")
    print("\nThen compare with:")
    print(f"  pw-play {INPUT_FILE}")


if __name__ == "__main__":
    main()
