import numpy as np


class SpectralNoiseReducer:

    def __init__(
        self,
        sample_rate=48000,
        frame_size=2048,
        hop_size=512,
        noise_search_duration=10.0,
        noise_update_rate=0.03,
        reduction_strength=0.55,
        minimum_gain=0.55,
        smoothing=0.85,
    ):

        self.sample_rate = sample_rate
        self.frame_size = frame_size
        self.hop_size = hop_size

        self.noise_search_duration = noise_search_duration
        self.noise_update_rate = noise_update_rate
        self.reduction_strength = reduction_strength
        self.minimum_gain = minimum_gain
        self.smoothing = smoothing

        self.window = np.hanning(
            frame_size
        ).astype(np.float32)

        self.previous_gain = np.ones(
            frame_size // 2 + 1,
            dtype=np.float32
        )

        self.noise_power = None

    # =========================================================
    # RESET STATE
    # =========================================================

    def reset(self):

        self.previous_gain = np.ones(
            self.frame_size // 2 + 1,
            dtype=np.float32
        )

        self.noise_power = None

    # =========================================================
    # NOISE ESTIMATION
    # =========================================================

    def estimate_noise(self, audio):

        audio = np.asarray(
            audio,
            dtype=np.float32
        ).reshape(-1)

        search_samples = min(
            len(audio),
            int(
                self.noise_search_duration
                * self.sample_rate
            )
        )

        search_audio = audio[
            :search_samples
        ]

        if len(search_audio) < self.frame_size:

            # For short audio, use the available
            # audio after zero padding.

            padded = np.pad(
                search_audio,
                (
                    0,
                    self.frame_size -
                    len(search_audio)
                )
            )

            spectrum = np.fft.rfft(
                padded * self.window
            )

            noise_power = (
                np.abs(spectrum) ** 2
            )

            self.noise_power = np.maximum(
                noise_power,
                1e-10
            )

            return self.noise_power

        frames = []
        energies = []

        for start in range(
            0,
            len(search_audio) -
            self.frame_size + 1,
            self.hop_size
        ):

            frame = search_audio[
                start:
                start + self.frame_size
            ]

            energy = np.mean(
                frame ** 2
            )

            energies.append(
                energy
            )

            spectrum = np.fft.rfft(
                frame * self.window
            )

            power = (
                np.abs(spectrum) ** 2
            )

            frames.append(
                power
            )

        energies = np.asarray(
            energies,
            dtype=np.float32
        )

        frames = np.asarray(
            frames,
            dtype=np.float32
        )

        if len(frames) == 0:

            padded = np.pad(
                search_audio,
                (
                    0,
                    max(
                        0,
                        self.frame_size -
                        len(search_audio)
                    )
                )
            )

            padded = padded[
                :self.frame_size
            ]

            spectrum = np.fft.rfft(
                padded * self.window
            )

            noise_power = (
                np.abs(spectrum) ** 2
            )

            self.noise_power = np.maximum(
                noise_power,
                1e-10
            )

            return self.noise_power

        # -----------------------------------------------------
        # Quietest 25% of frames
        # -----------------------------------------------------

        threshold = np.percentile(
            energies,
            25
        )

        quiet_frames = frames[
            energies <= threshold
        ]

        if len(quiet_frames) == 0:

            quiet_frames = frames

        noise_power = np.median(
            quiet_frames,
            axis=0
        )

        self.noise_power = np.maximum(
            noise_power,
            1e-10
        )

        return self.noise_power

    # =========================================================
    # SPEECH DETECTION
    # =========================================================

    def detect_speech(
        self,
        magnitude
    ):

        if self.noise_power is None:

            return True

        signal_power = (
            magnitude ** 2
        )

        average_snr = np.mean(
            signal_power /
            (
                self.noise_power +
                1e-10
            )
        )

        average_snr_db = (
            10 *
            np.log10(
                max(
                    average_snr,
                    1e-10
                )
            )
        )

        return average_snr_db > 4.0

    # =========================================================
    # PROCESS AUDIO
    # =========================================================

    def process(self, audio):

        audio = np.asarray(
            audio,
            dtype=np.float32
        ).reshape(-1)

        if len(audio) == 0:

            return audio

        original_length = len(audio)

        # -----------------------------------------------------
        # Estimate initial noise
        # -----------------------------------------------------

        self.estimate_noise(
            audio
        )

        # -----------------------------------------------------
        # Padding
        # -----------------------------------------------------

        if original_length < self.frame_size:

            pad_amount = (
                self.frame_size -
                original_length
            )

        else:

            remainder = (
                (
                    original_length -
                    self.frame_size
                )
                %
                self.hop_size
            )

            pad_amount = (
                self.hop_size -
                remainder
            ) % self.hop_size

        padded = np.pad(
            audio,
            (
                0,
                pad_amount
            )
        )

        enhanced = np.zeros_like(
            padded,
            dtype=np.float32
        )

        window_sum = np.zeros_like(
            padded,
            dtype=np.float32
        )

        # =====================================================
        # FRAME PROCESSING
        # =====================================================

        for start in range(
            0,
            len(padded) -
            self.frame_size + 1,
            self.hop_size
        ):

            frame = padded[
                start:
                start + self.frame_size
            ]

            windowed = (
                frame *
                self.window
            )

            spectrum = np.fft.rfft(
                windowed
            )

            magnitude = np.abs(
                spectrum
            )

            phase = np.angle(
                spectrum
            )

            signal_power = (
                magnitude ** 2
            )

            # -------------------------------------------------
            # Speech detection
            # -------------------------------------------------

            is_speech = self.detect_speech(
                magnitude
            )

            # -------------------------------------------------
            # Adaptive noise update
            # -------------------------------------------------

            if not is_speech:

                self.noise_power = (
                    (
                        1.0 -
                        self.noise_update_rate
                    )
                    *
                    self.noise_power
                    +
                    self.noise_update_rate
                    *
                    signal_power
                )

                self.noise_power = np.maximum(
                    self.noise_power,
                    1e-10
                )

            # -------------------------------------------------
            # SNR estimation
            # -------------------------------------------------

            snr = (
                signal_power /
                (
                    self.noise_power +
                    1e-10
                )
            )

            snr = np.maximum(
                snr - 1.0,
                0.0
            )

            # -------------------------------------------------
            # Wiener gain
            # -------------------------------------------------

            wiener_gain = (
                snr /
                (
                    snr + 1.0
                )
            )

            # -------------------------------------------------
            # Speech protection
            # -------------------------------------------------

            gain = (
                self.minimum_gain
                +
                (
                    1.0 -
                    self.minimum_gain
                )
                *
                wiener_gain
            )

            # -------------------------------------------------
            # Gentle suppression
            # -------------------------------------------------

            gain = (
                1.0
                -
                self.reduction_strength
                *
                (
                    1.0 -
                    gain
                )
            )

            # -------------------------------------------------
            # Strong speech components
            # -------------------------------------------------

            relative_power = (
                signal_power /
                (
                    self.noise_power +
                    1e-10
                )
            )

            strong_speech = (
                relative_power > 6.0
            )

            gain[strong_speech] = np.maximum(
                gain[strong_speech],
                0.85
            )

            # -------------------------------------------------
            # Limit gain
            # -------------------------------------------------

            gain = np.clip(
                gain,
                self.minimum_gain,
                1.0
            )

            # -------------------------------------------------
            # Temporal smoothing
            # -------------------------------------------------

            gain = (
                self.smoothing
                *
                self.previous_gain
                +
                (
                    1.0 -
                    self.smoothing
                )
                *
                gain
            )

            self.previous_gain = gain

            # -------------------------------------------------
            # Apply enhancement
            # -------------------------------------------------

            enhanced_spectrum = (
                magnitude
                *
                gain
                *
                np.exp(
                    1j * phase
                )
            )

            enhanced_frame = np.fft.irfft(
                enhanced_spectrum,
                n=self.frame_size
            )

            enhanced_frame *= (
                self.window
            )

            enhanced[
                start:
                start + self.frame_size
            ] += enhanced_frame

            window_sum[
                start:
                start + self.frame_size
            ] += (
                self.window ** 2
            )

        # =====================================================
        # OVERLAP ADD NORMALIZATION
        # =====================================================

        valid = (
            window_sum > 1e-8
        )

        enhanced[valid] /= (
            window_sum[valid]
        )

        enhanced = enhanced[
            :original_length
        ]

        # =====================================================
        # CLIPPING PROTECTION
        # =====================================================

        peak = np.max(
            np.abs(enhanced)
        )

        if peak > 0.98:

            enhanced = (
                enhanced /
                peak *
                0.95
            )

        return enhanced.astype(
            np.float32
        )