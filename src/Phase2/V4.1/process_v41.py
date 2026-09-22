import time
import numpy as np
import soundfile as sf
from pathlib import Path

from spectral_noise_reduction_v41 import SpectralNoiseReducer


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_DIR = PROJECT_ROOT / "input"
OUTPUT_DIR = PROJECT_ROOT / "output"

INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = INPUT_DIR / "test_original_v41.wav"
OUTPUT_FILE = OUTPUT_DIR / "test_enhanced_v41.wav"


# ============================================================
# HEADER
# ============================================================

print("=" * 60)
print("PHASE 2 - V4.1 SPEECH ENHANCEMENT")
print("=" * 60)

print(f"\nInput file : {INPUT_FILE}")
print(f"Output file: {OUTPUT_FILE}")


# ============================================================
# CHECK INPUT FILE
# ============================================================

if not INPUT_FILE.is_file():
    print("\nERROR: Input audio file was not found.")
    print(f"\nExpected file:\n{INPUT_FILE}")
    print("\nPlease run:")
    print("python test_audio.py")
    raise SystemExit(1)


# ============================================================
# LOAD AUDIO
# ============================================================

audio, sample_rate = sf.read(
    str(INPUT_FILE)
)

if audio.ndim > 1:
    audio = audio.mean(axis=1)

audio = audio.astype(
    np.float32
)


# ============================================================
# AUDIO INFORMATION
# ============================================================

print(
    f"\nSample rate: {sample_rate} Hz"
)

print(
    f"Duration: "
    f"{len(audio) / sample_rate:.2f} seconds"
)


# ============================================================
# V4.1 FEATURES
# ============================================================

print("\nV4.1 features:")
print("  - Automatic noise-frame selection")
print("  - Voice Activity Detection")
print("  - Adaptive noise estimation")
print("  - Wiener filtering")
print("  - Speech protection")
print("  - Temporal gain smoothing")


# ============================================================
# V4.1 SPEECH ENHANCER
# ============================================================

reducer = SpectralNoiseReducer(
    sample_rate=sample_rate,
    frame_size=2048,
    hop_size=512,
    noise_search_duration=10.0,
    noise_update_rate=0.03,
    reduction_strength=0.55,
    minimum_gain=0.55,
    smoothing=0.85,
)


# ============================================================
# PROCESS AUDIO
# ============================================================

print("\nProcessing audio...")

start = time.perf_counter()

enhanced = reducer.process(
    audio
)

processing_time = (
    time.perf_counter()
    - start
)

enhanced = np.asarray(
    enhanced,
    dtype=np.float32
)


# ============================================================
# FINAL OUTPUT LEVEL BOOST
# ============================================================
# This does NOT change the V4.1 enhancement algorithm.
# It only increases the final output level.

OUTPUT_GAIN = 3.0

print(
    f"\nApplying final output gain: "
    f"{OUTPUT_GAIN:.1f}x"
)

enhanced = enhanced * OUTPUT_GAIN


# ============================================================
# CLIPPING PROTECTION
# ============================================================

enhanced = np.clip(
    enhanced,
    -1.0,
    1.0
)


# ============================================================
# SAVE ENHANCED AUDIO
# ============================================================

sf.write(
    str(OUTPUT_FILE),
    enhanced,
    sample_rate,
    subtype="PCM_16"
)


# ============================================================
# AUDIO METRICS
# ============================================================

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


# ============================================================
# RESULTS
# ============================================================

print("\n" + "=" * 60)
print("V4.1 RESULTS")
print("=" * 60)

print(
    f"Original RMS    : "
    f"{original_rms:.6f}"
)

print(
    f"Enhanced RMS    : "
    f"{enhanced_rms:.6f}"
)

print(
    f"Original Peak   : "
    f"{original_peak:.6f}"
)

print(
    f"Enhanced Peak   : "
    f"{enhanced_peak:.6f}"
)

print(
    f"RMS change      : "
    f"{rms_change:+.2f} dB"
)

print(
    f"Output gain     : "
    f"{OUTPUT_GAIN:.1f}x"
)

print(
    f"Processing time : "
    f"{processing_time:.3f} seconds"
)

print(
    f"\nCreated:"
)

print(
    OUTPUT_FILE
)

print("\n" + "=" * 60)
print("PROCESSING COMPLETE")
print("=" * 60)