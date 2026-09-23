# 🎙️ Speech Enhancement and Noise Removal

> **Adaptive Hybrid Spectral Subtraction and Wiener Filtering for Single-Channel Speech Enhancement**

A speech enhancement project focused on reducing unwanted background noise while preserving speech quality. The project progresses from a basic DSP baseline to adaptive frequency-domain speech enhancement, with a proposed extension that combines spectral subtraction and Wiener filtering.

---

## 📌 Overview

Speech recorded in real-world environments is often contaminated by background noise such as fans, air conditioners, traffic, keyboards, and other environmental sounds.

The basic noisy-speech model is:

```text
y(t) = s(t) + n(t)
```

where:

- `y(t)` = observed noisy speech
- `s(t)` = desired speech
- `n(t)` = background noise

The project aims to estimate the unwanted noise from the available audio signal and produce enhanced speech.

---

## 🎯 Objectives

- Capture speech from an audio input.
- Analyze speech in the frequency domain.
- Estimate background noise adaptively.
- Reduce unwanted noise.
- Protect important speech components.
- Reconstruct enhanced speech.
- Support real-time audio processing.
- Develop a hybrid spectral-subtraction and Wiener-filtering extension.
- Evaluate the system using objective and subjective measures.

---

## 🏗️ Project Development

The project is developed in stages:

```text
Basic DSP
    ↓
Phase 1
    ↓
Adaptive Spectral Enhancement
    ↓
Phase 2 V4.2 / V4.3
    ↓
Proposed Hybrid Extension
    ↓
Testing and Evaluation
```

---

## 🔹 Phase 1: DSP Baseline

Phase 1 provides the initial signal-processing baseline.

### Pipeline

```text
Input WAV
   ↓
Stereo → Mono
   ↓
Normalization
   ↓
Controlled Noise Addition
   ↓
FFT Analysis
   ↓
Butterworth Low-Pass Filter
   ↓
Enhanced Audio
```

### Main Processing

- FFT-based analysis
- Sixth-order Butterworth low-pass filter
- 4 kHz cutoff
- Zero-phase filtering
- SNR comparison
- Waveform and spectrum visualization

The project documentation records a baseline test with:

```text
Input SNR  = 8.18 dB
Output SNR = 14.86 dB
Improvement = 6.69 dB
```

These values depend on the specific recording and noise conditions.

---

## 🔹 Phase 2: Adaptive Speech Enhancement

Phase 2 moves from basic filtering toward adaptive frequency-domain speech enhancement.

The current V4.2/V4.3 processing includes:

- Short-time FFT
- Hann windowing
- Initial noise estimation
- Speech probability estimation
- Adaptive noise tracking
- Wiener-type gain calculation
- Frequency-dependent speech protection
- Strong-component protection
- Temporal gain smoothing
- IFFT reconstruction
- Overlap-add
- Peak limiting

### Current Pipeline

```text
Noisy Audio
     ↓
Frame Audio
     ↓
Hann Window
     ↓
FFT
     ↓
Initial Noise Estimation
     ↓
Speech Probability
     ↓
Adaptive Noise Tracking
     ↓
Wiener Gain
     ↓
Speech Protection
     ↓
Gain Smoothing
     ↓
IFFT
     ↓
Overlap-Add
     ↓
Enhanced Audio
```

---

## 🚀 Proposed Extension

### Adaptive Hybrid Spectral Subtraction and Wiener Filtering

The proposed extension combines two frequency-domain noise-reduction techniques:

```text
Spectral Subtraction
        +
Wiener Filtering
        ↓
    Hybrid Gain
```

### Why Hybrid?

**Spectral subtraction** provides direct noise suppression but can introduce musical-noise artifacts or speech distortion when the noise estimate is inaccurate.

**Wiener filtering** provides smoother frequency-dependent attenuation but may leave residual noise or suppress weak speech.

The proposed hybrid approach aims to combine the useful characteristics of both methods.

---

## 🔬 Proposed Processing

```text
Noisy Single-Channel Speech
          ↓
Framing + Windowing
          ↓
FFT
          ↓
Speech Probability
          ↓
Adaptive Noise Estimation
          ↓
Spectral Subtraction Gain
          +
Wiener Gain
          ↓
Hybrid Gain
          ↓
Speech Protection
          ↓
Spectral Floor + Smoothing
          ↓
IFFT
          ↓
Overlap-Add
          ↓
Enhanced Speech
```

A proposed hybrid gain can be represented as:

```text
G_H(k) = λG_SS(k) + (1 - λ)G_W(k)
```

where:

- `G_SS(k)` = spectral subtraction gain
- `G_W(k)` = Wiener gain
- `λ` = weighting factor

The hybrid method is a **proposed extension** and should not be considered fully implemented or validated until its code and experimental results are completed.

---

## 🎙️ Single-Channel Processing

The proposed hybrid system is intended to use a single microphone signal:

```text
Microphone
    ↓
Noisy Speech
    ↓
Enhancement
    ↓
Enhanced Speech
```

No separate noise-reference microphone is required for the proposed single-channel approach.

---

## ⚡ Real-Time Application

The repository also contains a separate real-time LMS adaptive noise-cancellation application.

Its architecture is:

```text
Primary Microphone
       +
Noise Reference Microphone
       ↓
LMS Adaptive Noise Cancellation
       ↓
Enhanced Audio
       ↓
PipeWire Virtual Sink
```

### Important

The current LMS real-time application uses two microphone inputs. Therefore, it is different from the proposed single-channel hybrid architecture.

---

## 📊 Evaluation

The system can be evaluated using:

| Metric | Purpose |
|---|---|
| SNR | Measures signal-to-noise relationship |
| STOI | Measures speech intelligibility |
| SI-SDR | Measures speech enhancement/separation quality |
| PESQ | Measures perceived speech quality when applicable |
| Latency | Measures real-time processing delay |
| CPU Usage | Measures computational load |
| Memory Usage | Measures resource consumption |

Additional evaluation includes:

- Waveform comparison
- Spectrogram comparison
- Listening tests
- Noise-condition testing
- Real-time stability testing

---

## 🧪 Test Conditions

The system should be tested under different conditions:

### Clean Speech

Check whether speech remains clear without unnecessary distortion.

### Stationary Noise

Examples:

- Fan
- AC
- Constant background noise

### Non-Stationary Noise

Examples:

- Traffic
- Changing environmental noise
- Sudden background sounds

### Low-SNR Conditions

Test speech under strong background noise.

### Multiple Speakers

Test target speech together with another speaker.

> Suppressing another speaker while preserving a target speaker is a more difficult speech-separation/target-speaker problem and must be experimentally demonstrated rather than assumed.

### Real-Time

Check:

- Latency
- Audio dropouts
- Stability
- CPU usage
- Memory usage
- Output quality

---

## 📚 Base Paper

The project is based on:

**C.-T. Lin, "Single-Channel Speech Enhancement in Variable Noise-Level Environment," IEEE Transactions on Systems, Man, and Cybernetics – Part A: Systems and Humans, 2003.**

DOI:

```text
10.1109/TSMCA.2003.811115
```

### Base Paper Focus

The paper addresses single-channel speech enhancement under variable noise conditions and provides concepts related to:

- Noise estimation
- Variable noise levels
- Speech/noise boundary detection
- Spectral subtraction
- Adaptive enhancement

The proposed hybrid method extends the project toward combining spectral subtraction and Wiener filtering.

---

## 🧠 Key Technical Concepts

### FFT

Converts short-time audio frames from the time domain into the frequency domain.

```text
Y(k) = FFT{y(n)}
```

### Adaptive Noise Estimation

Updates the estimated noise spectrum as the background environment changes.

```text
N_t(k) = αN_(t-1)(k) + (1 - α)|Y_t(k)|²
```

### Spectral Subtraction

Estimates speech by reducing the estimated noise spectrum.

```text
P_S(k) = max(P_Y(k) - βP_N(k), γP_Y(k))
```

### Wiener Filtering

Calculates a frequency-dependent gain using estimated speech and noise power.

```text
G_W(k) = P_S(k) / (P_S(k) + P_N(k))
```

### Gain Smoothing

Reduces rapid gain changes and helps control unwanted artifacts.

### IFFT and Overlap-Add

Reconstruct the enhanced time-domain audio from processed frequency-domain frames.

---

## 📁 Project Structure

The repository contains the main project components for:

```text
SpeechEnhancementandnoiseremoval/
│
├── src/
│   ├── Phase 1 processing
│   ├── Phase 2 processing
│   └── Real-time processing
│
├── docs/
│   └── Project documentation
│
├── results/
│   └── Generated results and analysis
│
├── README.md
└── Other project files
```

> The exact structure may change as development continues. The repository should be treated as the source of truth for the current implementation.

---

## ⚠️ Current Limitations

- Noise estimation can become difficult when noise changes rapidly.
- Speech and noise can overlap in the same frequency range.
- Single-channel processing cannot directly measure a separate noise reference.
- Multiple-speaker suppression is more difficult than ordinary background-noise reduction.
- Spectral subtraction can introduce musical-noise artifacts if not controlled.
- The proposed hybrid method requires experimental parameter tuning.
- The current real-time LMS implementation uses a separate noise-reference microphone.
- A completed ML training/inference pipeline is not part of the current inspected implementation.

---

## 🛣️ Future Work

- Implement the spectral subtraction gain.
- Integrate spectral subtraction with the current Wiener-based enhancement.
- Develop and test hybrid gain weighting.
- Optimize adaptive parameters.
- Evaluate under changing noise conditions.
- Improve real-time latency.
- Perform detailed objective evaluation.
- Add suitable ML-based enhancement if required.
- Compare DSP and ML approaches.
- Improve target-speaker preservation where appropriate.

---

## 📌 Current Status

### Existing

- [x] Phase 1 DSP baseline
- [x] FFT processing
- [x] Adaptive noise estimation
- [x] Speech probability estimation
- [x] Wiener-type enhancement
- [x] Speech protection
- [x] Gain smoothing
- [x] IFFT reconstruction
- [x] Overlap-add
- [x] Real-time LMS prototype

### Proposed / In Progress

- [ ] Spectral subtraction gain
- [ ] Hybrid gain
- [ ] Adaptive hybrid weighting
- [ ] Hybrid real-time integration
- [ ] Complete comparison with V4.3
- [ ] Objective evaluation
- [ ] Listening evaluation
- [ ] ML integration

---

## 👨‍💻 Development

### Main Technologies

- Python
- NumPy
- SciPy
- Librosa
- SoundDevice
- Matplotlib
- PyTorch / ML tools when integrated
- PipeWire for the Linux real-time prototype
- Git
- GitHub

---

## 🔄 Overall System Concept

```text
                 NOISY SPEECH
                      │
                      ▼
              Audio Acquisition
                      │
                      ▼
             Pre-processing
                      │
                      ▼
              FFT / Framing
                      │
                      ▼
          Adaptive Noise Estimation
                      │
             ┌────────┴────────┐
             ▼                 ▼
      Spectral Subtraction   Wiener
             │                 │
             └────────┬────────┘
                      ▼
                 Hybrid Gain
                      │
                      ▼
              Speech Protection
                      │
                      ▼
                  Smoothing
                      │
                      ▼
                     IFFT
                      │
                      ▼
                Overlap-Add
                      │
                      ▼
               ENHANCED SPEECH
```

---

## 🎓 Project Summary

This project investigates single-channel speech enhancement using adaptive frequency-domain processing.

The current system progresses from a basic DSP baseline to adaptive Wiener-based speech enhancement. The proposed extension combines spectral subtraction and Wiener filtering to create a hybrid noise-reduction method.

The central challenge is to reduce background noise while preserving speech quality, particularly when the noise environment changes.

The final system will be evaluated using objective measurements, audio analysis, and real-time testing.

---

## 📖 Reference

C.-T. Lin, "Single-Channel Speech Enhancement in Variable Noise-Level Environment," IEEE Transactions on Systems, Man, and Cybernetics – Part A: Systems and Humans, vol. 33, no. 1, 2003, pp. 137–144.

DOI: `10.1109/TSMCA.2003.811115`

---

## 📜 Project Status

**Project:** Speech Enhancement and Noise Removal

**Focus:** Adaptive Single-Channel Speech Enhancement

**Current Development:** Phase 2 / Hybrid Extension

**Repository:** SpeechEnhancementandnoiseremoval
