"""The phase noise class generates colored phase noise samples."""

import numpy as np
import scipy.signal

from simulation.radar.components.noise import GaussianNoise
from simulation.radar.components.radar import Radar
from simulation.radar.components.samples import Samples
from simulation.radar.components.target import Target
from utils import constants

# Number of samples of the phase noise spectrum.
NUM_PHASE_NOISE_SPECTRUM_SAMPLES = 100000


class PhaseNoise:
    """Represents complex phase noise.

    Each element of the offsets array is a 2-tuple containing the frequency
    offset and the corresponding noise level in dBc/Hz.
    The frequency offsets should be strictly increasing, and the phase noise
    level values should be negative.
    """

    def __init__(self,
                 radar: Radar = None,
                 offsets: list[tuple[float, float]] = None,
                 fs: float = None):
        if radar is None and (offsets is None or fs is None):
            raise ValueError(
                "Either a radar or the phase noise offsets and sampling "
                "frequency must be provided.")
        self.offsets = (radar.phase_noise_offsets
                        if radar is not None else offsets)
        self.fs = radar.fs if radar is not None else fs

    def generate_noise_samples(self, amplitude: float, length: int) -> Samples:
        """Generates noise samples.

        Args:
            amplitude: Signal amplitude.
            length: Signal length.
            target: Target.

        Returns:
            Complex phase noise samples.
        """
        # Calcaluate the phase noise power spectrum from the phase noise
        # profile.
        frequencies = np.linspace(0, self.fs / 2, length, endpoint=False)
        frequencies[-1] = self.fs / 2
        phase_noise_level = (
            self._interpolate_phase_noise_level(length, frequencies) +
            constants.power2db(self._get_phase_noise_factor(frequencies)))

        # Integrate the phase noise PSD to find the noise power within each
        # noise sample.
        resolution_bandwidth = self.fs / length
        phase_noise_power = phase_noise_level + constants.power2db(
            resolution_bandwidth)

        # Generate the FIR filter.
        fir_filter = scipy.signal.firwin2(length,
                                          frequencies,
                                          constants.db2mag(phase_noise_power),
                                          antisymmetric=True,
                                          fs=self.fs)

        # Generate white Gaussian noise and filter it.
        gaussian_noise = GaussianNoise.generate_noise_samples(
            length, amplitude / np.sqrt(length))
        # Use a circular convolution.
        phase_noise = np.fft.ifft(
            np.fft.fft(gaussian_noise) * np.fft.fft(fir_filter))
        return phase_noise

    def calculate_phase_noise_level(self) -> tuple[np.ndarray, np.ndarray]:
        """Calculates the phase noise power spectrum density in dBc/Hz.

        Returns:
            A 2-tuple consisting of the frequency offsets and the corresponding
            phase noise level in dBc/Hz.
        """
        num_points = self._get_num_interpolation_points()
        frequencies = np.concatenate(
            ([0],
             np.logspace(0,
                         np.log10(self.fs / 2),
                         num=NUM_PHASE_NOISE_SPECTRUM_SAMPLES,
                         base=10)))
        phase_noise_level = (
            self._interpolate_phase_noise_level(num_points, frequencies) +
            constants.power2db(self._get_phase_noise_factor(frequencies)))
        return frequencies, phase_noise_level

    def _get_num_interpolation_points(self) -> int:
        """Calculates the number of interpolation points.

        The number of taps is the largest power of 2, such that the frequency
        resolution is smaller than or equal to the smallest phase noise
        frequency offset divided by 4, i.e., fs / 2 / num_taps <=
        min(phase_noise_offset) / 4.

        See https://www.mathworks.com/help/comm/ref/comm.phasenoise-system-object.html
        for more details on the FIR filter.

        Returns:
            The number of taps in the FIR filter.
        """
        num_points_float = self.fs / 2 / (self.offsets[0][0] / 4)
        num_points = int(2**np.ceil(np.log2(num_points_float)))
        return num_points

    def _interpolate_phase_noise_level(self, num_taps: float,
                                       frequencies: np.ndarray) -> np.ndarray:
        """Calculates the LO phase noise level in dBc/Hz at the given frequency
        offsets using interpolation.

        See https://www.mathworks.com/help/comm/ref/comm.phasenoise-system-object.html
        for more details on the phase noise interpolation.

        Args:
            offsets: List of 2-tuples containing the frequency offset and noise
              level.
            fs: Sampling frequency in Hz.
            num_taps: Number of taps in the FIR filter.
            frequencies: List of frequency offsets in Hz.

        Returns:
            An array consisting of the phase noise level in dBc/Hz at each
            frequency offset.
        """
        # Calculate the phase noise level at the frequency resolution.
        frequency_resolution = self.fs / 2 / num_taps
        # According to https://www.mathworks.com/help/comm/ref/comm.phasenoise-system-object.html,
        # phase noise has a 1/f^3 characteristic from the frequency resolution
        # to the smallest frequency offset.
        phase_noise_level_at_frequency_resolution = (
            self.offsets[0][1] +
            3 * constants.power2db(self.offsets[0][0] / frequency_resolution))

        # Interpolate the phase noise level.
        phase_noise_offsets = [(frequency_resolution,
                                phase_noise_level_at_frequency_resolution),
                               *self.offsets]
        phase_noise_levels = np.zeros(shape=frequencies.shape)
        for phase_noise_offset_index, (
                phase_noise_offset,
                phase_noise_level) in enumerate(phase_noise_offsets):
            if phase_noise_offset_index == 0:
                indices = frequencies <= phase_noise_offset
                phase_noise_levels[indices] = phase_noise_level
                continue
            previous_phase_noise_offset, previous_phase_noise_level = (
                phase_noise_offsets[phase_noise_offset_index - 1])
            indices = ((frequencies > previous_phase_noise_offset) &
                       (frequencies <= phase_noise_offset))
            phase_noise_levels[indices] = (
                (phase_noise_level * constants.power2db(
                    frequencies[indices] / previous_phase_noise_offset) +
                 previous_phase_noise_level * constants.power2db(
                     phase_noise_offset / frequencies[indices])) /
                constants.power2db(
                    phase_noise_offset / previous_phase_noise_offset))
        phase_noise_levels[(
            frequencies
            > phase_noise_offsets[-1][0])] = phase_noise_offsets[-1][1]
        return phase_noise_levels

    def _get_phase_noise_factor(self, frequencies: np.ndarray) -> np.ndarray:
        """Calculates the phase noise factor at each frequency offset.

        Args:
            frequencies: Frequency offsets in Hz.

        Returns:
            An array corresponding to the phase noise factor at each frequency
            offset.
        """
        return np.ones(shape=frequencies.shape)


class IFPhaseNoise(PhaseNoise):
    """Represents complex IF phase noise.

    Each element of the offsets array is a 2-tuple containing the frequency
    offset and the corresponding noise level in dBc/Hz.
    The frequency offsets should be strictly increasing, and the phase noise
    level values should be negative.
    """

    def __init__(self,
                 target: Target,
                 radar: Radar = None,
                 offsets: list[tuple[float, float]] = None,
                 fs: float = None):
        self.target = target
        super().__init__(radar, offsets, fs)

    def _get_phase_noise_factor(self, frequencies: np.ndarray) -> np.ndarray:
        """Calculates the phase noise factor at each frequency offset.

        Args:
            frequencies: Frequency offsets in Hz.

        Returns:
            An array corresponding to the phase noise factor at each frequency
            offset.
        """
        if_phase_noise_factor = np.zeros(shape=frequencies.shape)
        tau = 2 * self.target.range / Radar.c

        # Handle the case where f * tau <= 1/2.
        indices = (frequencies * tau) <= (1 / 2)
        if_phase_noise_factor[indices] = 2 * (
            1 - np.cos(2 * np.pi * frequencies[indices] * tau))

        # Handle the case where f * tau > 1/2.
        indices = (frequencies * tau) > (1 / 2)
        if_phase_noise_factor[indices] = 4
        return if_phase_noise_factor
