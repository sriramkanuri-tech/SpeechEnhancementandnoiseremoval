import time
import numpy as np
import soundfile as sf

from spectral_noise_reduction import SpectralNoiseReducer


INPUT_FILE = "../output/test_original.wav"
OUTPUT_FILE = "../output/test_enhanced_v42.wav"


print("=" * 60)
print("PHASE 2 - V4.2 SPEECH ENHANCEMENT")
print("=" * 60)

audio, sample_rate = sf.read(
    INPUT_FILE
)

if audio.ndim > 1:
    audio = audio.mean(axis=1)

audio = audio.astype(
    np.float32
)

print(
    f"\nSample rate: {sample_rate} Hz"
)

print(
    f"Duration: "
    f"{len(audio) / sample_rate:.2f} seconds"
)

print("\nV4.2 features:")
print("  - Automatic quiet-frame noise estimation")
print("  - Soft Voice Activity Detection")
print("  - Adaptive noise tracking")
print("  - Wiener filtering")
print("  - Speech protection")
print("  - Temporal gain smoothing")

reducer = SpectralNoiseReducer(
    sample_rate=sample_rate,
    frame_size=2048,
    hop_size=512,
    noise_update_rate=0.02,
    reduction_strength=0.50,
    minimum_gain=0.60,
    smoothing=0.88,
)

start = time.perf_counter()

enhanced = reducer.process(
    audio
)

processing_time = (
    time.perf_counter()
    - start
)

sf.write(
    OUTPUT_FILE,
    enhanced,
    sample_rate,
    subtype="PCM_16"
)

original_rms = np.sqrt(
    np.mean(audio ** 2)
)

enhanced_rms = np.sqrt(
    np.mean(enhanced ** 2)
)

original_peak = np.max(
    np.abs(audio)
)

enhanced_peak = np.max(
    np.abs(enhanced)
)

rms_change = (
    20
    * np.log10(
        enhanced_rms
        /
        max(
            original_rms,
            1e-10
        )
    )
)

print("\n" + "=" * 60)
print("V4.2 RESULTS")
print("=" * 60)

print(
    f"Original RMS : "
    f"{original_rms:.6f}"
)

print(
    f"Enhanced RMS : "
    f"{enhanced_rms:.6f}"
)

print(
    f"Original peak: "
    f"{original_peak:.6f}"
)

print(
    f"Enhanced peak: "
    f"{enhanced_peak:.6f}"
)

print(
    f"RMS change   : "
    f"{rms_change:+.2f} dB"
)

print(
    f"Processing time: "
    f"{processing_time:.3f} seconds"
)

print(
    f"\nCreated: {OUTPUT_FILE}"
)
