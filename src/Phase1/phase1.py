import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy import signal


# ============================================================
# SPEECH ENHANCEMENT AND NOISE REMOVAL
# PHASE 1
# ============================================================

INPUT_FILE = "input/speech.wav"

OUTPUT_FILE = "output/enhanced_speech.wav"

PLOT_FILE = "plots/phase1_results.png"


# ============================================================
# 1. LOAD SPEECH
# ============================================================

sample_rate, speech = wavfile.read(INPUT_FILE)

print("\n==========================================")
print(" SPEECH ENHANCEMENT AND NOISE REMOVAL")
print(" PHASE 1")
print("==========================================")

print(f"Sample rate : {sample_rate} Hz")
print(f"Samples     : {len(speech)}")
print(f"Channels    : {speech.shape[1] if speech.ndim == 2 else 1}")


# ============================================================
# 2. CONVERT STEREO TO MONO
# ============================================================

if speech.ndim == 2:
    speech = speech.mean(axis=1)


# Convert to floating point
speech = speech.astype(np.float64)


# Normalize
max_value = np.max(np.abs(speech))

if max_value > 0:
    speech = speech / max_value


# ============================================================
# 3. ADD ARTIFICIAL WHITE NOISE
# ============================================================

np.random.seed(42)

noise = np.random.normal(
    0,
    1,
    len(speech)
)

noise = noise / np.max(np.abs(noise))


# Noise strength
noise_strength = 0.20

noisy_speech = speech + noise_strength * noise


# Normalize noisy signal
max_value = np.max(np.abs(noisy_speech))

if max_value > 0:
    noisy_speech = noisy_speech / max_value


print("\nArtificial noise added.")


# ============================================================
# 4. SNR FUNCTION
# ============================================================

def calculate_snr(clean_signal, test_signal):

    noise_signal = clean_signal - test_signal

    signal_power = np.mean(clean_signal ** 2)

    noise_power = np.mean(noise_signal ** 2)

    if noise_power == 0:
        return float("inf")

    return 10 * np.log10(
        signal_power / noise_power
    )


# ============================================================
# 5. SNR BEFORE FILTERING
# ============================================================

snr_before = calculate_snr(
    speech,
    noisy_speech
)

print(f"SNR before filtering : {snr_before:.2f} dB")


# ============================================================
# 6. FFT OF NOISY SPEECH
# ============================================================

N = len(noisy_speech)

fft_noisy = np.fft.rfft(noisy_speech)

frequency = np.fft.rfftfreq(
    N,
    1 / sample_rate
)

magnitude_noisy = np.abs(fft_noisy) / N


print("FFT analysis completed.")


# ============================================================
# 7. DESIGN BUTTERWORTH LOW-PASS FILTER
# ============================================================

filter_order = 6

cutoff_frequency = 4000


b, a = signal.butter(
    filter_order,
    cutoff_frequency,
    btype="lowpass",
    fs=sample_rate
)


print("Digital Butterworth low-pass filter designed.")
print(f"Filter order : {filter_order}")
print(f"Cutoff       : {cutoff_frequency} Hz")


# ============================================================
# 8. FILTER NOISY SPEECH
# ============================================================

enhanced_speech = signal.filtfilt(
    b,
    a,
    noisy_speech
)


# Normalize
max_value = np.max(np.abs(enhanced_speech))

if max_value > 0:
    enhanced_speech = enhanced_speech / max_value


print("Noise filtering completed.")


# ============================================================
# 9. SNR AFTER FILTERING
# ============================================================

snr_after = calculate_snr(
    speech,
    enhanced_speech
)

snr_improvement = snr_after - snr_before


print(f"SNR after filtering  : {snr_after:.2f} dB")
print(f"SNR improvement      : {snr_improvement:.2f} dB")


# ============================================================
# 10. FFT OF ENHANCED SPEECH
# ============================================================

fft_enhanced = np.fft.rfft(
    enhanced_speech
)

magnitude_enhanced = (
    np.abs(fft_enhanced) / N
)


# ============================================================
# 11. TIME AXIS
# ============================================================

time = np.arange(N) / sample_rate


# ============================================================
# 12. CREATE RESULTS FIGURE
# ============================================================

fig, axes = plt.subplots(
    3,
    2,
    figsize=(14, 10)
)


# Original speech
axes[0, 0].plot(time, speech)

axes[0, 0].set_title(
    "Original Clean Speech"
)

axes[0, 0].set_xlabel("Time (seconds)")
axes[0, 0].set_ylabel("Amplitude")
axes[0, 0].grid()


# Noisy speech
axes[1, 0].plot(time, noisy_speech)

axes[1, 0].set_title(
    "Noisy Speech"
)

axes[1, 0].set_xlabel("Time (seconds)")
axes[1, 0].set_ylabel("Amplitude")
axes[1, 0].grid()


# Enhanced speech
axes[2, 0].plot(time, enhanced_speech)

axes[2, 0].set_title(
    "Enhanced Speech"
)

axes[2, 0].set_xlabel("Time (seconds)")
axes[2, 0].set_ylabel("Amplitude")
axes[2, 0].grid()


# Noisy frequency spectrum
axes[0, 1].plot(
    frequency,
    magnitude_noisy
)

axes[0, 1].set_title(
    "FFT Spectrum - Noisy Speech"
)

axes[0, 1].set_xlabel("Frequency (Hz)")
axes[0, 1].set_ylabel("Magnitude")

axes[0, 1].set_xlim(
    0,
    sample_rate / 2
)

axes[0, 1].grid()


# Enhanced frequency spectrum
axes[1, 1].plot(
    frequency,
    magnitude_enhanced
)

axes[1, 1].set_title(
    "FFT Spectrum - Enhanced Speech"
)

axes[1, 1].set_xlabel("Frequency (Hz)")
axes[1, 1].set_ylabel("Magnitude")

axes[1, 1].set_xlim(
    0,
    sample_rate / 2
)

axes[1, 1].grid()


# SNR result
axes[2, 1].axis("off")

axes[2, 1].text(
    0.1,
    0.7,
    f"SNR Before Filtering : {snr_before:.2f} dB",
    fontsize=14
)

axes[2, 1].text(
    0.1,
    0.5,
    f"SNR After Filtering  : {snr_after:.2f} dB",
    fontsize=14
)

axes[2, 1].text(
    0.1,
    0.3,
    f"SNR Improvement      : {snr_improvement:.2f} dB",
    fontsize=14
)


fig.suptitle(
    "Speech Enhancement and Noise Removal - Phase 1",
    fontsize=16
)

plt.tight_layout()

plt.savefig(
    PLOT_FILE,
    dpi=200
)

plt.show()


# ============================================================
# 13. SAVE ENHANCED AUDIO
# ============================================================

output_audio = np.int16(
    np.clip(enhanced_speech, -1, 1) * 32767
)

wavfile.write(
    OUTPUT_FILE,
    sample_rate,
    output_audio
)


# ============================================================
# 14. FINAL REPORT
# ============================================================

print("\n==========================================")
print(" PHASE 1 COMPLETE")
print("==========================================")

print(f"Input audio       : {INPUT_FILE}")
print(f"Output audio      : {OUTPUT_FILE}")
print(f"Results plot      : {PLOT_FILE}")

print("------------------------------------------")

print(
    f"SNR before        : {snr_before:.2f} dB"
)

print(
    f"SNR after         : {snr_after:.2f} dB"
)

print(
    f"SNR improvement   : {snr_improvement:.2f} dB"
)

print("==========================================")
