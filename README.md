# Speech Enhancement and Noise Removal

A real-time speech enhancement system designed to reduce background noise and improve speech clarity.

## Project Overview

This project focuses on developing a speech enhancement system that processes an audio signal and reduces unwanted background noise.

The system currently includes a traditional signal-processing based approach using spectral noise reduction and is being extended with machine learning based speech enhancement.

## Features

- Real-time audio processing
- Background noise reduction
- Voice Activity Detection
- Adaptive noise estimation
- Wiener filtering
- Speech protection
- Temporal gain smoothing
- Audio waveform comparison
- Spectrogram comparison
- Audio performance measurements
- Test Mode for recorded audio
- Meeting Mode for real-time processing

## System Pipeline

```text
Microphone
    ↓
Audio Input
    ↓
Noise Estimation
    ↓
Voice Activity Detection
    ↓
Spectral Noise Reduction
    ↓
Speech Enhancement
    ↓
Output Gain
    ↓
Enhanced Speech
    ↓
Speaker
