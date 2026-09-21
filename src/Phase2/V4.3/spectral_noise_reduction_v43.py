import numpy as np


class SpectralNoiseReducer:

    def __init__(
        self,
        sample_rate=48000,
        frame_size=2048,
        hop_size=512,
        noise_update_rate=0.025,
        reduction_strength=0.45,
        minimum_gain=0.60,
        smoothing=0.90,
    ):
        self.sample_rate = sample_rate
        self.frame_size = frame_size
        self.hop_size = hop_size

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

    def initialize_noise(self, audio):

        audio = np.asarray(
            audio,
            dtype=np.float32
        )

        frames = []
        energies = []

        for start in range(
            0,
            len(audio) - self.frame_size + 1,
            self.hop_size
        ):

            frame = audio[
                start:start + self.frame_size
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

            power = np.abs(
                spectrum
            ) ** 2

            frames.append(power)

        if len(frames) == 0:
            raise ValueError(
                "Audio is too short for noise estimation."
            )

        energies = np.asarray(
            energies
        )

        frames = np.asarray(
            frames
        )

        # Use the quietest 20% of frames.
        threshold = np.percentile(
            energies,
            20
        )

        quiet_frames = frames[
            energies <= threshold
        ]

        if len(quiet_frames) == 0:
            quiet_frames = frames

        self.noise_power = np.median(
            quiet_frames,
            axis=0
        )

        self.noise_power = np.maximum(
            self.noise_power,
            1e-10
        )

    def calculate_speech_probability(
        self,
        magnitude
    ):

        signal_power = (
            magnitude ** 2
        )

        snr_ratio = (
            signal_power
            /
            (self.noise_power + 1e-10)
        )

        energy_ratio = np.mean(
            snr_ratio
        )

        energy_db = (
            10
            * np.log10(
                max(
                    energy_ratio,
                    1e-10
                )
            )
        )

        active_bins = np.mean(
            snr_ratio > 2.5
        )

        energy_score = np.clip(
            (energy_db - 2.0) / 8.0,
            0.0,
            1.0
        )

        activity_score = np.clip(
            (active_bins - 0.08) / 0.30,
            0.0,
            1.0
        )

        probability = (
            0.7 * energy_score
            +
            0.3 * activity_score
        )

        return float(
            np.clip(
                probability,
                0.0,
                1.0
            )
        )

    def process(self, audio):

        audio = np.asarray(
            audio,
            dtype=np.float32
        ).reshape(-1)

        original_length = len(audio)

        self.initialize_noise(
            audio
        )

        if original_length < self.frame_size:

            pad_amount = (
                self.frame_size
                - original_length
            )

        else:

            remainder = (
                (
                    original_length
                    - self.frame_size
                )
                % self.hop_size
            )

            pad_amount = (
                self.hop_size
                - remainder
            ) % self.hop_size

        padded = np.pad(
            audio,
            (0, pad_amount)
        )

        enhanced = np.zeros_like(
            padded,
            dtype=np.float32
        )

        window_sum = np.zeros_like(
            padded,
            dtype=np.float32
        )

        frequencies = np.fft.rfftfreq(
            self.frame_size,
            d=1.0 / self.sample_rate
        )

        for start in range(
            0,
            len(padded) - self.frame_size + 1,
            self.hop_size
        ):

            frame = padded[
                start:start + self.frame_size
            ]

            windowed = (
                frame * self.window
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

            speech_probability = (
                self.calculate_speech_probability(
                    magnitude
                )
            )

            noise_weight = (
                1.0
                - speech_probability
            )

            update_rate = (
                self.noise_update_rate
                * noise_weight
            )

            if update_rate > 0:

                self.noise_power = (
                    (1.0 - update_rate)
                    * self.noise_power
                    +
                    update_rate
                    * signal_power
                )

                self.noise_power = np.maximum(
                    self.noise_power,
                    1e-10
                )

            snr = (
                signal_power
                /
                (self.noise_power + 1e-10)
            )

            snr = np.maximum(
                snr - 1.0,
                0.0
            )

            wiener_gain = (
                snr
                /
                (snr + 1.0)
            )

            speech_protection = (
                0.60
                +
                0.35
                * speech_probability
            )

            gain = (
                speech_protection
                +
                (
                    1.0
                    - speech_protection
                )
                * wiener_gain
            )

            gain = (
                1.0
                -
                self.reduction_strength
                * (1.0 - gain)
            )

            # Frequency-dependent protection.
            #
            # Low frequencies:
            # allow moderate suppression.
            #
            # Speech frequencies:
            # protect the signal more strongly.
            #
            # Very high frequencies:
            # allow slightly stronger suppression.

            low_frequency = (
                frequencies < 150
            )

            speech_band = (
                (frequencies >= 150)
                &
                (frequencies <= 5000)
            )

            high_frequency = (
                frequencies > 5000
            )

            gain[low_frequency] = np.maximum(
                gain[low_frequency],
                0.55
            )

            gain[speech_band] = np.maximum(
                gain[speech_band],
                0.70
            )

            gain[high_frequency] = np.maximum(
                gain[high_frequency],
                0.60
            )

            # Strong speech components receive
            # additional protection.

            strong_components = (
                snr > 5.0
            )

            gain[strong_components] = np.maximum(
                gain[strong_components],
                0.92
            )

            gain = np.clip(
                gain,
                self.minimum_gain,
                1.0
            )

            gain = (
                self.smoothing
                * self.previous_gain
                +
                (1.0 - self.smoothing)
                * gain
            )

            self.previous_gain = gain

            enhanced_spectrum = (
                magnitude
                * gain
                * np.exp(
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
                start:start + self.frame_size
            ] += enhanced_frame

            window_sum[
                start:start + self.frame_size
            ] += self.window ** 2

        valid = (
            window_sum > 1e-8
        )

        enhanced[valid] /= (
            window_sum[valid]
        )

        enhanced = enhanced[
            :original_length
        ]

        peak = np.max(
            np.abs(enhanced)
        )

        if peak > 0.98:

            enhanced = (
                enhanced
                / peak
                * 0.95
            )

        return enhanced.astype(
            np.float32
        )
