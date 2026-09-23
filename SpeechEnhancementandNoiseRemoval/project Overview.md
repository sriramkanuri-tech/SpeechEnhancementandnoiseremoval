# 🎙️ Speech Enhancement and Noise Removal - Complete Project Notes

````
# 🎙️ Speech Enhancement and Noise Removal
## Complete Project Notes

> **Proposed Title:** Adaptive Hybrid Spectral Subtraction and Wiener Filtering for Single-Channel Speech Enhancement

---

# 1. 📌 Project Overview

The project focuses on developing a speech enhancement system that receives speech contaminated by background noise and produces an enhanced speech signal with reduced unwanted noise.

The project progresses from a basic Digital Signal Processing (DSP) implementation toward an adaptive frequency-domain speech enhancement system and a proposed hybrid extension.

---

## Project Domain

- Digital Signal Processing
- Speech Enhancement
- Noise Removal
- Frequency-Domain Processing
- Real-Time Audio Processing
- Adaptive Filtering

---

# 2. 🏷️ What the Title Means

## Adaptive Hybrid Spectral Subtraction and Wiener Filtering for Single-Channel Speech Enhancement

The title describes the **proposed extension** of the project.

It is **not the title of the base paper**.

---

## Adaptive

"Adaptive" means that the system changes its noise estimation and processing behavior according to the changing background noise.

Real-world noise is not always constant.

Examples:

- Fan noise
- AC noise
- Traffic
- People moving
- Changing environmental noise

Therefore, the system should continuously update its estimate of the background noise.

---

## Hybrid

"Hybrid" means that two frequency-domain noise-reduction techniques are combined:

```text
Spectral Subtraction
        +
Wiener Filtering
        ↓
   Hybrid Gain
````

The purpose is to combine the noise-suppression characteristics of both methods.

---

## Spectral Subtraction

Spectral subtraction estimates the noise spectrum and subtracts it from the noisy speech spectrum.

Conceptually:

```
Noisy Spectrum
      -
Noise Spectrum
      ↓
Estimated Speech Spectrum
```

It is computationally simple, but aggressive subtraction can introduce speech distortion and musical-noise artifacts.

---

## Wiener Filtering

Wiener filtering calculates a frequency-dependent gain based on the estimated relationship between speech and noise.

It provides smoother attenuation than direct spectral subtraction.

---

## Single-Channel

Single-channel means that the proposed enhancement system uses **one microphone signal**.

```
Microphone
    ↓
Noisy Speech
    ↓
Enhancement
    ↓
Enhanced Speech
```

There is no separate microphone whose only purpose is to capture noise.

---

## Speech Enhancement

The objective is not simply to remove everything except speech.

The actual goal is:

```
Reduce Noise
     +
Preserve Speech
     ↓
Enhanced Speech
```

---

# 3. 🎯 Main Problem

A noisy speech signal can be represented as:

y(t) = s(t) + n(t)

where:

- y(t) = observed noisy speech
- s(t) = desired speech
- n(t) = background noise

The main problem is estimating the desired speech signal from the noisy signal.

---

## Why is this difficult?

In a single-channel system:

```
Microphone
    ↓
Speech + Noise
```

We do not have a separate recording containing only the noise.

The system therefore has to estimate the noise from the same microphone signal.

The problem becomes more difficult when:

- Noise changes with time
- Speech and noise overlap in frequency
- Noise occurs while the person is speaking
- Noise estimation becomes inaccurate
- Multiple speakers are present

---

# 4. 🎯 Project Objectives

## Primary Objective

Develop a real-time speech enhancement system that reduces unwanted background noise while preserving speech quality.

## Specific Objectives

1. Capture speech using a microphone.
2. Process the incoming audio signal.
3. Convert audio into the frequency domain.
4. Estimate background noise.
5. Adapt the noise estimate when the environment changes.
6. Reduce unwanted noise.
7. Protect important speech components.
8. Reconstruct enhanced speech.
9. Support real-time processing.
10. Develop the proposed hybrid spectral subtraction + Wiener method.
11. Compare the proposed method with the current system.
12. Evaluate the system using objective and subjective measurements.

---

# 5. 📚 Base Paper

## Title

**Single-Channel Speech Enhancement in Variable Noise-Level Environment**

## Author

**Chin-Teng Lin**

## Publication

IEEE Transactions on Systems, Man, and Cybernetics – Part A: Systems and Humans

## Year

2003

## DOI

10.1109/TSMCA.2003.811115

---

## Main Problem Addressed by the Paper

The base paper focuses on single-channel speech enhancement when the background noise level changes.

Traditional subtractive speech enhancement algorithms often assume that the background noise is fixed or slowly varying.

However, real-world background noise can change.

This can cause:

```
Incorrect Speech/Noise Detection
            ↓
Incorrect Noise Estimation
            ↓
Poor Speech Enhancement
```

---

# 6. 🧠 Important Concepts from the Base Paper

The base paper uses several important concepts.

## 6.1 Single-Channel Enhancement

The system operates using one speech/noise recording.

---

## 6.2 RTF

The paper uses a refined time-frequency parameter for extracting useful frequency information.

---

## 6.3 RSONFIN

The paper uses a Recurrent Self-Organizing Neural Fuzzy Inference Network for word-boundary detection.

Its purpose is to distinguish speech regions from noise regions under variable noise conditions.

---

## 6.4 MiFre

MiFre stands for **Minimum Frequency Energy**.

It is used to estimate the changing background noise level.

The important idea is that noise estimation is not restricted only to speech pauses.

The paper allows noise information to be estimated during speech segments when the background noise is changing.

---

## 6.5 Spectral Subtraction

The base paper uses subtractive-type speech enhancement.

The basic concept is:

```
Noisy Spectrum
      -
Estimated Noise Spectrum
      ↓
Enhanced Spectrum
```

---

# 7. 🔬 Base Paper Experimental Setup

The supplied paper reports:

- Sampling rate: 8 kHz
- Frame size: 240 samples
- Frame duration: 30 ms
- Overlap: 50%
- 100 noisy Mandarin speech sentences
- Noise from NOISE-ROM-0
- Input SNR values from 0 to 15 dB

The paper reports that estimating noise during speech segments improved output SNR under variable background noise conditions.

> These are the base-paper experimental conditions. They are different from the current project's 48 kHz Phase 2 processing.

---

# 8. 🏗️ Project Development

The project has progressed through multiple stages.

```
Basic DSP
   ↓
Phase 1
   ↓
Adaptive Spectral Enhancement
   ↓
Phase 2 V4.2
   ↓
Phase 2 V4.3
   ↓
Proposed Hybrid Extension
```

---

# 9. 🔹 Phase 1

Phase 1 provides the basic DSP baseline.

## Processing

```
Input WAV
   ↓
Convert Stereo → Mono
   ↓
Normalize
   ↓
Add Controlled Noise
   ↓
FFT Analysis
   ↓
Butterworth Low-Pass Filter
   ↓
IFFT / Reconstruction
   ↓
Enhanced Audio
```

---

## Phase 1 Filter

The implementation uses:

- Sixth-order Butterworth low-pass filter
- 4 kHz cutoff
- Zero-phase filtering

---

## Phase 1 Evaluation

The project documentation records one test where:

```
Input SNR  = 8.18 dB
Output SNR = 14.86 dB

Improvement = 6.69 dB
```

These values depend on the specific recording and noise conditions.

They should therefore be treated as a recorded baseline result rather than a universal performance value.

---

# 10. 🔹 Phase 2 V4.2 / V4.3

Phase 2 moves from basic filtering toward adaptive frequency-domain enhancement.

The current system uses:

- Short-time FFT
- Adaptive noise estimation
- Speech probability
- Wiener-type filtering
- Speech protection
- Temporal smoothing
- IFFT
- Overlap-add

---

# 11. 🔄 Current V4.3 Pipeline

```
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
Frequency-Dependent Protection
     ↓
Strong Speech Protection
     ↓
Temporal Gain Smoothing
     ↓
IFFT
     ↓
Overlap-Add
     ↓
Peak Limiting
     ↓
Enhanced Audio
```

---

# 12. 🎛️ Current V4.3 Parameters

The Phase 2 test utilities use:

- Mono audio
- 48 kHz sample rate
- 2048-point FFT
- 512-sample hop size
- Hann window

---

# 13. 🔊 Framing and Windowing

Continuous audio is divided into short overlapping frames.

Each frame is multiplied by a window function.

Example:

```
Continuous Audio
       ↓
Short Frames
       ↓
Hann Window
       ↓
FFT
```

Windowing reduces discontinuities at frame boundaries.

---

# 14. 📈 FFT Processing

The Fast Fourier Transform converts the audio from the time domain into the frequency domain.

Y(k) = FFT{y(n)}

The frequency representation contains:

- Magnitude
- Phase

The magnitude is used for noise estimation and gain calculation.

The original phase can be retained for reconstruction.

---

# 15. 🌐 Adaptive Noise Estimation

The current system initially estimates noise from relatively quiet frames.

The Phase 2 implementation selects approximately the quietest 20% of analyzed frames and uses the median spectrum to form an initial noise-power estimate.

Conceptually:

```
Audio Frames
     ↓
Find Quiet Frames
     ↓
Estimate Noise Spectrum
     ↓
Initial Noise Model
```

---

# 16. 🗣️ Speech Probability

The current system calculates a soft estimate of whether a frame contains speech.

It uses information such as:

- Spectral energy
- Proportion of frequency bins above the noise estimate

Conceptually:

```
Current Spectrum
      ↓
Speech Analysis
      ↓
Speech Probability
```

The result is not simply a hard speech/no-speech decision.

---

# 17. 🔄 Adaptive Noise Tracking

The noise estimate changes over time.

A general recursive model is:

N_t(k) = αN_(t-1)(k) + (1-α)|Y_t(k)|²

The current implementation makes the update slower when speech probability is high.

Conceptually:

```
Noise Frame
    ↓
Faster Noise Update

Speech Frame
    ↓
Slower Noise Update
```

This helps prevent the speaker's voice from being incorrectly learned as background noise.

---

# 18. 🎚️ Current Wiener-Type Gain

The current V4.3 system calculates a Wiener-type gain using an estimated frequency-dependent SNR.

Conceptually:

```
Estimated Speech Power
          +
Estimated Noise Power
          ↓
       SNR Estimate
          ↓
      Wiener Gain
```

The gain determines how strongly each frequency component is attenuated.

---

# 19. 🛡️ Speech Protection

The current system includes speech-protection mechanisms.

These include:

- Frequency-dependent minimum gains
- Strong spectral-component protection
- Gain floors

The purpose is to prevent important speech components from being excessively suppressed.

---

# 20. 🔄 Gain Smoothing

Rapid changes in gain can produce unnatural sound and musical-noise artifacts.

Therefore, the gain is smoothed over time.

G~_t(k) = αG~_(t-1)(k) + (1-α)G_t(k)

Conceptually:

```
Current Gain
     +
Previous Gain
     ↓
Smoothed Gain
```

---

# 21. 🔊 Audio Reconstruction

After applying the gain:

S_hat(k) = G(k)Y(k)

The enhanced spectrum is converted back into the time domain.

```
Enhanced Spectrum
       ↓
      IFFT
       ↓
Enhanced Frames
       ↓
Overlap-Add
       ↓
Enhanced Speech
```

---

# 22. 💻 Real-Time Application

The repository also contains a separate real-time application using LMS adaptive noise cancellation.

The real-time application uses:

```
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

---

## Important Distinction

This real-time LMS system uses **two microphone inputs**.

Therefore:

> It should not be described as the proposed single-channel implementation.

The proposed single-channel hybrid method should work using one microphone signal.

---

# 23. 🚀 Proposed Extension

The next proposed development is:

> **Adaptive Hybrid Spectral Subtraction and Wiener Filtering for Single-Channel Speech Enhancement**

The extension adds spectral subtraction to the current adaptive Wiener-based framework.

---

# 24. 🏗️ Proposed Architecture

```
Noisy Single-Channel Speech
          ↓
Framing + Windowing
          ↓
FFT
          ↓
Speech Activity / Probability
          ↓
Adaptive Noise Estimation
          ↓
 ┌──────────────────────┐
 │ Spectral Subtraction │
 │ Gain Calculation     │
 └──────────┬───────────┘
            │
            +
            │
 ┌──────────▼───────────┐
 │ Wiener Gain          │
 │ Calculation          │
 └──────────┬───────────┘
            ↓
      Hybrid Gain
            ↓
     Speech Protection
            ↓
   Spectral Floor
            ↓
      Gain Smoothing
            ↓
           IFFT
            ↓
       Overlap-Add
            ↓
     Enhanced Speech
```

---

# 25. ➖ Spectral Subtraction Stage

The proposed spectral subtraction stage estimates the speech power:

P_S(k) = max(P_Y(k) - βP_N(k), γP_Y(k))

where:

- P_Y(k) = noisy signal power
- P_N(k) = estimated noise power
- β = subtraction factor
- γ = spectral-floor factor

A corresponding gain can be calculated as:

G_SS(k) = max(1 - βP_N(k)/P_Y(k), G_min²)

---

# 26. 🎚️ Wiener Stage

The proposed Wiener gain can be represented as:

P_S(k) = max(P_Y(k) - P_N(k), 0)

G_W(k) = P_S(k) / (P_S(k) + P_N(k))

This provides smoother attenuation according to the estimated speech-to-noise relationship.

---

# 27. 🔀 Hybrid Gain

The two gains are combined:

G_H(k) = λG_SS(k) + (1-λ)G_W(k)

where:

- G_SS(k) = spectral subtraction gain
- G_W(k) = Wiener gain
- λ = weighting factor

Example:

```
λ = 0.7
→ More spectral-subtraction influence

λ = 0.5
→ Equal contribution

λ = 0.3
→ More Wiener-filter influence
```

The first experiment can use a fixed λ.

A later version can make λ adaptive according to estimated SNR.

---

# 28. 🛡️ Proposed Speech Protection

The hybrid gain should preserve the existing speech-protection concept.

Conceptually:

G_final(k) = max(G_H(k), G_protection(k))

This prevents important speech components from being excessively attenuated.

The exact thresholds should be experimentally validated.

---

# 29. 🎵 Musical-Noise Reduction

Spectral subtraction can produce residual musical-noise artifacts.

Possible causes:

- Abrupt gain changes
- Isolated spectral peaks
- Incorrect noise estimation
- Excessive subtraction

The project therefore uses:

- Spectral floor
- Temporal smoothing
- Frequency smoothing where required
- Speech protection

The purpose is to obtain smoother and more natural enhanced speech.

---

# 30. 🔬 Why Combine Spectral Subtraction and Wiener Filtering?

## Spectral Subtraction

### Advantage

- Direct noise suppression
- Computationally simple

### Limitation

- Can create musical noise
- Can distort speech if the estimate is inaccurate

---

## Wiener Filtering

### Advantage

- Smooth frequency-dependent attenuation
- Based on estimated speech/noise relationship

### Limitation

- Can leave residual noise
- Can suppress weak speech when noise estimation is inaccurate

---

## Hybrid Approach

The proposed hybrid method attempts to combine:

```
Stronger Noise Suppression
          +
Smoother Attenuation
          ↓
       Hybrid
```

However, the hybrid method must be experimentally validated.

It should **not** be claimed to be superior until testing is completed.

---

# 31. 🔬 Current Implementation vs Proposed Extension

|Component|Current V4.3|Proposed|
|---|---|---|
|Single-channel input|✓|✓|
|FFT|✓|✓|
|Windowing|✓|✓|
|Initial noise estimation|✓|✓|
|Speech probability|✓|✓|
|Adaptive noise tracking|✓|✓|
|Wiener gain|✓|✓|
|Speech protection|✓|✓|
|Gain smoothing|✓|✓|
|Spectral subtraction gain|❌|✓|
|Hybrid gain|❌|✓|
|Adaptive hybrid weighting|❌|Future|
|ML enhancement|❌|Future|

---

# 32. 🧪 Testing Plan

The proposed method should be compared with the current V4.3 system using the same recordings and noise conditions.

---

## Test 1: Clean Speech

### Input

Speech with minimal background noise.

### Check

- Speech clarity
- Distortion
- Voice naturalness

---

## Test 2: Stationary Noise

Examples:

- Fan
- AC
- Constant background noise

### Check

Whether the system reduces the noise while maintaining speech.

---

## Test 3: Non-Stationary Noise

Examples:

- Changing environmental noise
- Traffic
- Sudden background sounds

### Check

Whether adaptive noise estimation follows the changing environment.

---

## Test 4: Low SNR

Use speech with strong background noise.

### Check

Whether the system can preserve speech under difficult conditions.

---

## Test 5: Multiple Speakers

```
Target Speaker
      +
Other Speaker
      ↓
Enhancement
```

### Important

This is a harder speech-separation/target-speaker problem.

The system should not be claimed to remove another speaker unless the experiment demonstrates it.

---

## Test 6: Real-Time

Use live microphone input.

Check:

- Latency
- Audio dropouts
- Stability
- CPU usage
- Memory usage
- Speech quality

---

# 33. 📊 Evaluation Metrics

## SNR

Signal-to-Noise Ratio.

Used to measure the relationship between desired speech and noise.

---

## STOI

Short-Time Objective Intelligibility.

Used to estimate speech intelligibility.

---

## SI-SDR

Scale-Invariant Signal-to-Distortion Ratio.

Can be used when an appropriate reference signal is available.

---

## PESQ

Perceptual Evaluation of Speech Quality.

Used where the evaluation setup and reference conditions are appropriate.

---

## Latency

Measures:

```
Speech Input
     ↓
Processing
     ↓
Enhanced Output
```

The delay should be low enough for practical real-time use.

---

## CPU and Memory

Measure computational requirements of the system.

---

## Spectrogram Comparison

Compare:

```
Noisy Speech Spectrogram
          ↓
Enhanced Speech Spectrogram
```

This helps visualize which frequency components were attenuated.

---

# 34. ⚠️ Technical Limitations

## 1. Single-Channel Noise Estimation

The system cannot directly measure a separate noise signal.

It must estimate noise from the observed microphone signal.

---

## 2. Changing Noise

Rapidly changing noise can make noise estimation difficult.

---

## 3. Speech and Noise Overlap

If noise occupies the same frequency range as speech, frequency-domain filtering cannot perfectly separate them.

---

## 4. Other Speakers

Another person's speech is not ordinary stationary noise.

Removing another speaker while preserving a target speaker is a harder speech-separation problem.

---

## 5. Phase 1 Filter

The 4 kHz low-pass filter should not be described as removing all noise above 4 kHz.

It is a baseline filtering approach.

---

## 6. Real-Time LMS System

The current LMS real-time implementation uses two microphones.

Therefore it is different from the proposed single-channel architecture.

---

## 7. Machine Learning

The inspected project source does not contain a completed ML training/inference pipeline.

ML should therefore be treated as future work until the model is actually integrated and tested.

---

# 35. 🧠 Important Project Understanding

The project should be understood as three separate levels:

## Level 1: Existing Base

```
Base Paper
Single-Channel
Variable Noise
Spectral Subtraction
Adaptive Noise Estimation
```

↓

## Level 2: Current Implementation

```
FFT
+
Adaptive Noise Estimation
+
Speech Probability
+
Wiener Filtering
+
Speech Protection
+
Smoothing
```

↓

## Level 3: Proposed Extension

```
Current Adaptive Framework
          +
Spectral Subtraction
          +
Wiener Filtering
          ↓
     Hybrid Method
```