from pathlib import Path

import numpy as np
import soundfile as sf

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_DIR = PROJECT_ROOT / "input"
OUTPUT_DIR = PROJECT_ROOT / "output"
PLOTS_DIR = PROJECT_ROOT / "plots"

INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

INPUT_FILE = INPUT_DIR / "test_original_v41.wav"
OUTPUT_FILE = OUTPUT_DIR / "test_enhanced_v41.wav"


# ============================================================
# HEADER
# ============================================================

print("=" * 60)
print("GENERATING AUDIO COMPARISON PLOTS")
print("=" * 60)


# ============================================================
# CHECK FILES
# ============================================================

if not INPUT_FILE.is_file():
    print("\nERROR: Original audio was not found.")
    print(INPUT_FILE)
    raise SystemExit(1)

if not OUTPUT_FILE.is_file():
    print("\nERROR: Enhanced audio was not found.")
    print(OUTPUT_FILE)
    raise SystemExit(1)


# ============================================================
# LOAD ORIGINAL AUDIO
# ============================================================

original, original_sr = sf.read(
    str(INPUT_FILE)
)

if original.ndim > 1:
    original = original.mean(axis=1)

original = original.astype(np.float32)


# ============================================================
# LOAD ENHANCED AUDIO
# ============================================================

enhanced, enhanced_sr = sf.read(
    str(OUTPUT_FILE)
)

if enhanced.ndim > 1:
    enhanced = enhanced.mean(axis=1)

enhanced = enhanced.astype(np.float32)


# ============================================================
# AUDIO METRICS
# ============================================================

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

rms_change = (
    20
    * np.log10(
        enhanced_rms /
        max(original_rms, 1e-10)
    )
)


# ============================================================
# 1. WAVEFORM
# ============================================================

print("\nCreating waveform plot...")

original_time = (
    np.arange(len(original)) /
    original_sr
)

enhanced_time = (
    np.arange(len(enhanced)) /
    enhanced_sr
)

fig, axes = plt.subplots(
    2,
    1,
    figsize=(14, 8)
)

axes[0].plot(
    original_time,
    original,
    linewidth=0.6
)

axes[0].set_title(
    "Original Speech Waveform"
)

axes[0].set_xlabel(
    "Time (seconds)"
)

axes[0].set_ylabel(
    "Amplitude"
)

axes[0].grid(
    True,
    alpha=0.3
)


axes[1].plot(
    enhanced_time,
    enhanced,
    linewidth=0.6
)

axes[1].set_title(
    "V4.1 Enhanced Speech Waveform"
)

axes[1].set_xlabel(
    "Time (seconds)"
)

axes[1].set_ylabel(
    "Amplitude"
)

axes[1].grid(
    True,
    alpha=0.3
)

fig.tight_layout()

waveform_file = (
    PLOTS_DIR /
    "waveform_comparison.png"
)

fig.savefig(
    str(waveform_file),
    dpi=150,
    format="png"
)

plt.close(fig)

print(
    f"Created: {waveform_file}"
)


# ============================================================
# 2. SPECTROGRAM
# ============================================================

print("\nCreating spectrogram plot...")

fig, axes = plt.subplots(
    2,
    1,
    figsize=(14, 9)
)

axes[0].specgram(
    original,
    Fs=original_sr,
    NFFT=2048,
    noverlap=1536
)

axes[0].set_title(
    "Original Speech Spectrogram"
)

axes[0].set_xlabel(
    "Time (seconds)"
)

axes[0].set_ylabel(
    "Frequency (Hz)"
)


axes[1].specgram(
    enhanced,
    Fs=enhanced_sr,
    NFFT=2048,
    noverlap=1536
)

axes[1].set_title(
    "V4.1 Enhanced Speech Spectrogram"
)

axes[1].set_xlabel(
    "Time (seconds)"
)

axes[1].set_ylabel(
    "Frequency (Hz)"
)

fig.tight_layout()

spectrogram_file = (
    PLOTS_DIR /
    "spectrogram_comparison.png"
)

fig.savefig(
    str(spectrogram_file),
    dpi=120,
    format="png"
)

plt.close(fig)

print(
    f"Created: {spectrogram_file}"
)


# ============================================================
# 3. AUDIO METRICS
# ============================================================

print("\nCreating audio metrics plot...")

labels = [
    "Original\nRMS",
    "Enhanced\nRMS",
    "Original\nPeak",
    "Enhanced\nPeak"
]

values = [
    original_rms,
    enhanced_rms,
    original_peak,
    enhanced_peak
]

fig, ax = plt.subplots(
    figsize=(10, 6)
)

ax.bar(
    labels,
    values
)

ax.set_title(
    "Original vs V4.1 Enhanced Audio"
)

ax.set_ylabel(
    "Amplitude"
)

ax.grid(
    axis="y",
    alpha=0.3
)

fig.tight_layout()


# ------------------------------------------------------------
# IMPORTANT:
# Use a temporary filename for the third plot.
# ------------------------------------------------------------

temp_metrics_file = (
    PLOTS_DIR /
    "audio_metrics_temp.png"
)

final_metrics_file = (
    PLOTS_DIR /
    "audio_metrics.png"
)

# Remove old temporary file if it exists
if temp_metrics_file.exists():
    temp_metrics_file.unlink()

# Remove old final file if it exists
if final_metrics_file.exists():
    final_metrics_file.unlink()


fig.savefig(
    str(temp_metrics_file),
    dpi=150,
    format="png"
)

plt.close(fig)

print(
    f"Created: {temp_metrics_file}"
)


# ============================================================
# RENAME TEMPORARY FILE
# ============================================================

temp_metrics_file.rename(
    final_metrics_file
)

print(
    f"Created: {final_metrics_file}"
)


# ============================================================
# FINAL RESULTS
# ============================================================

print("\n" + "=" * 60)
print("PLOT GENERATION COMPLETE")
print("=" * 60)

print(
    f"\nOriginal RMS    : "
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
    f"RMS Change      : "
    f"{rms_change:+.2f} dB"
)

print("\nPlots created successfully:")

print(
    f"1. {waveform_file}"
)

print(
    f"2. {spectrogram_file}"
)

print(
    f"3. {final_metrics_file}"
)

print("\n" + "=" * 60)