#!/usr/bin/env python3

import matplotlib

# Important for Linux/headless/background plot generation.
# Prevents GUI backend problems.
matplotlib.use("Agg")

import numpy as np
import matplotlib.pyplot as plt

from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

PLOTS_DIR = PROJECT_ROOT / "plots"

PLOTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# HELPER
# ============================================================

def _prepare_audio(audio):
    """
    Convert audio to a clean mono float32 NumPy array.
    """

    audio = np.asarray(
        audio,
        dtype=np.float32
    )

    if audio.ndim > 1:
        audio = np.mean(
            audio,
            axis=1
        )

    return audio.reshape(-1)


# ============================================================
# WAVEFORM PLOT
# ============================================================

def create_waveform_plot(
    original,
    enhanced,
    sample_rate
):
    """
    Create original vs enhanced waveform comparison.

    Output:
        Phase2/plots/waveform_comparison.png
    """

    original = _prepare_audio(
        original
    )

    enhanced = _prepare_audio(
        enhanced
    )

    original_time = (
        np.arange(len(original))
        / sample_rate
    )

    enhanced_time = (
        np.arange(len(enhanced))
        / sample_rate
    )

    fig, axes = plt.subplots(
        2,
        1,
        figsize=(14, 8),
        sharex=False
    )

    # --------------------------------------------------------
    # ORIGINAL
    # --------------------------------------------------------

    axes[0].plot(
        original_time,
        original,
        linewidth=0.7
    )

    axes[0].set_title(
        "Original Audio Waveform"
    )

    axes[0].set_ylabel(
        "Amplitude"
    )

    axes[0].grid(
        True,
        alpha=0.3
    )

    # --------------------------------------------------------
    # ENHANCED
    # --------------------------------------------------------

    axes[1].plot(
        enhanced_time,
        enhanced,
        linewidth=0.7
    )

    axes[1].set_title(
        "V4.1 Enhanced Audio Waveform"
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

    fig.suptitle(
        "Speech Enhancement and Noise Removal - Waveform Comparison",
        fontsize=14,
        fontweight="bold"
    )

    fig.tight_layout()

    output_path = (
        PLOTS_DIR /
        "waveform_comparison.png"
    )

    fig.savefig(
        str(output_path),
        dpi=150,
        bbox_inches="tight"
    )

    plt.close(fig)

    print(
        f"Created: {output_path}"
    )

    return output_path


# ============================================================
# SPECTROGRAM PLOT
# ============================================================

def create_spectrogram_plot(
    original,
    enhanced,
    sample_rate
):
    """
    Create original vs enhanced spectrogram comparison.

    Output:
        Phase2/plots/spectrogram_comparison.png
    """

    original = _prepare_audio(
        original
    )

    enhanced = _prepare_audio(
        enhanced
    )

    fig, axes = plt.subplots(
        2,
        1,
        figsize=(14, 9)
    )

    # --------------------------------------------------------
    # ORIGINAL SPECTROGRAM
    # --------------------------------------------------------

    axes[0].specgram(
        original,
        Fs=sample_rate,
        NFFT=2048,
        noverlap=1536
    )

    axes[0].set_title(
        "Original Audio Spectrogram"
    )

    axes[0].set_ylabel(
        "Frequency (Hz)"
    )

    axes[0].set_ylim(
        0,
        min(
            sample_rate / 2,
            12000
        )
    )

    # --------------------------------------------------------
    # ENHANCED SPECTROGRAM
    # --------------------------------------------------------

    axes[1].specgram(
        enhanced,
        Fs=sample_rate,
        NFFT=2048,
        noverlap=1536
    )

    axes[1].set_title(
        "V4.1 Enhanced Audio Spectrogram"
    )

    axes[1].set_xlabel(
        "Time (seconds)"
    )

    axes[1].set_ylabel(
        "Frequency (Hz)"
    )

    axes[1].set_ylim(
        0,
        min(
            sample_rate / 2,
            12000
        )
    )

    fig.suptitle(
        "Speech Enhancement and Noise Removal - Spectrogram Comparison",
        fontsize=14,
        fontweight="bold"
    )

    fig.tight_layout()

    output_path = (
        PLOTS_DIR /
        "spectrogram_comparison.png"
    )

    fig.savefig(
        str(output_path),
        dpi=150,
        bbox_inches="tight"
    )

    plt.close(fig)

    print(
        f"Created: {output_path}"
    )

    return output_path


# ============================================================
# AUDIO METRICS PLOT
# ============================================================

def create_metrics_plot(
    original,
    enhanced
):
    """
    Create RMS and peak comparison plot.

    Output:
        Phase2/plots/audio_metrics.png
    """

    original = _prepare_audio(
        original
    )

    enhanced = _prepare_audio(
        enhanced
    )

    # --------------------------------------------------------
    # RMS
    # --------------------------------------------------------

    original_rms = float(
        np.sqrt(
            np.mean(
                original ** 2
            )
        )
    )

    enhanced_rms = float(
        np.sqrt(
            np.mean(
                enhanced ** 2
            )
        )
    )

    # --------------------------------------------------------
    # PEAK
    # --------------------------------------------------------

    original_peak = float(
        np.max(
            np.abs(original)
        )
    )

    enhanced_peak = float(
        np.max(
            np.abs(enhanced)
        )
    )

    # --------------------------------------------------------
    # RMS CHANGE
    # --------------------------------------------------------

    rms_change_db = (
        20 *
        np.log10(
            enhanced_rms /
            max(
                original_rms,
                1e-10
            )
        )
    )

    # --------------------------------------------------------
    # PLOT
    # --------------------------------------------------------

    labels = [
        "Original",
        "Enhanced"
    ]

    rms_values = [
        original_rms,
        enhanced_rms
    ]

    peak_values = [
        original_peak,
        enhanced_peak
    ]

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(12, 5)
    )

    # --------------------------------------------------------
    # RMS
    # --------------------------------------------------------

    axes[0].bar(
        labels,
        rms_values
    )

    axes[0].set_title(
        "RMS Level"
    )

    axes[0].set_ylabel(
        "RMS"
    )

    axes[0].grid(
        axis="y",
        alpha=0.3
    )

    # --------------------------------------------------------
    # PEAK
    # --------------------------------------------------------

    axes[1].bar(
        labels,
        peak_values
    )

    axes[1].set_title(
        "Peak Amplitude"
    )

    axes[1].set_ylabel(
        "Peak"
    )

    axes[1].grid(
        axis="y",
        alpha=0.3
    )

    fig.suptitle(
        "V4.1 Audio Metrics Comparison",
        fontsize=14,
        fontweight="bold"
    )

    fig.text(
        0.5,
        0.01,
        f"RMS Change: {rms_change_db:+.2f} dB",
        ha="center",
        fontsize=11
    )

    fig.tight_layout(
        rect=(
            0,
            0.04,
            1,
            1
        )
    )

    # --------------------------------------------------------
    # SAVE TEMPORARILY
    # --------------------------------------------------------

    temp_path = (
        PLOTS_DIR /
        "audio_metrics_temp.png"
    )

    final_path = (
        PLOTS_DIR /
        "audio_metrics.png"
    )

    fig.savefig(
        str(temp_path),
        dpi=150,
        bbox_inches="tight"
    )

    plt.close(fig)

    # --------------------------------------------------------
    # REPLACE OLD FILE
    # --------------------------------------------------------

    try:

        if final_path.exists():
            final_path.unlink()

        temp_path.replace(
            final_path
        )

    except Exception:

        # Fallback if replacement is not possible.
        final_path = temp_path

    print(
        f"Created: {final_path}"
    )

    return final_path


# ============================================================
# STANDALONE TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print(
        "V4.1 PLOT MODULE TEST"
    )
    print("=" * 60)

    print(
        f"\nProject root:\n{PROJECT_ROOT}"
    )

    print(
        f"\nPlots directory:\n{PLOTS_DIR}"
    )

    print(
        "\nAvailable functions:"
    )

    print(
        "  create_waveform_plot()"
    )

    print(
        "  create_spectrogram_plot()"
    )

    print(
        "  create_metrics_plot()"
    )

    print(
        "\nPlot module loaded successfully."
    )

    print(
        "=" * 60
    )
