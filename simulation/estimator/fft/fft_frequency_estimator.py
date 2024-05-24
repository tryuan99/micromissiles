"""The FFT frequency estimator estimates the frequencies within a signal using
the FFT.
"""

from enum import Enum, auto

import numpy as np

from simulation.estimator.frequency_estimator import FrequencyEstimator
from simulation.radar.components.peak_selector import PeakSelector
from simulation.radar.components.samples import Samples
from utils.regression.parabolic_regression import ParabolicRegression

# Guard length of 2 FFT bins.
FFT_NUM_BINS_GUARD_LENGTH = 2


class FftWindow(Enum):
    """FFT window enumeration."""
    RECTANGULAR = auto()
    HANN = auto()
    HAMMING = auto()
    BLACKMAN = auto()


class FftFrequencyEstimator(FrequencyEstimator):
    """Interface for an FFT frequency estimator."""

    def __init__(self, samples: Samples | np.ndarray, fs: float,
                 fft_length: int, window: np.ndarray) -> None:
        super().__init__(samples, fs)
        self.fft_resolution_factor = fft_length / self.size
        self.samples = self._perform_fft(self.samples, fft_length, window)

    def _bin_index_to_frequency(
            self, bin_indices: np.ndarray | float) -> np.ndarray | float:
        """Converts the bin indices to the corresponding frequencies.

        Args:
            bin_indices: Bin indices.

        Returns:
            The frequencies in Hz corresponding to the bins.
        """
        frequencies = bin_indices * self.fs / self.size
        # Account for negative frequencies.
        frequencies[frequencies >= self.fs / 2] -= self.fs
        return frequencies

    @staticmethod
    def _perform_fft(samples: np.ndarray, fft_length: int,
                     window: np.ndarray) -> np.ndarray:
        """Performs the FFT on the samples.

        Args:
            samples: Samples.
            fft_length: FFT length.
            window: Window.
        """
        return np.fft.fft(samples * window, fft_length)


class FftPeakFrequencyEstimator(FftFrequencyEstimator):
    """FFT frequency estimator by identifying the peaks in the FFT spectrum."""

    def __init__(self, samples: Samples, fs: float, fft_length: int,
                 window: np.ndarray) -> None:
        super().__init__(samples, fs, fft_length, window)

    def estimate_single_frequency(self) -> float:
        """Estimates a single frequency.

        Returns:
            The estimated frequency in Hz.
        """
        return self.estimate_multiple_frequencies(num_frequencies=1)[0]

    def estimate_multiple_frequencies(self, num_frequencies: int) -> np.ndarray:
        """Estimates multiple frequencies.

        Args:
            num_frequencies: Number of frequencies.

        Returns:
            The estimated frequencies in Hz.
        """
        bin_indices = self._find_bins_with_peaks(num_frequencies)
        corrected_bin_indices = self._correct_bin_indices(bin_indices)
        return self._bin_index_to_frequency(corrected_bin_indices)

    def _find_bins_with_peaks(self, num_peaks: int) -> np.ndarray:
        """Finds the bins corresponding to the peaks in the FFT spectrum.

        Args:
            num_peaks: Number of peaks.

        Returns:
            The bin indices corresponding to the peaks in the FFT spectrum.
        """
        # Use a guard length of 2 DFT bins.
        peak_selector = PeakSelector(self.samples,
                                     guard_length=int(
                                         np.ceil(FFT_NUM_BINS_GUARD_LENGTH *
                                                 self.fft_resolution_factor)))
        bin_indices = np.array(
            peak_selector.get_k_largest_peaks_index(num_peaks))[0]
        return bin_indices

    def _correct_bin_indices(self, bin_indices: np.ndarray) -> np.ndarray:
        """Correct the bin indices corresponding to the peaks in the FFT
        spectrum.

        Args:
            bin_indices: Bin indices corresponding to the peaks in the FFT
              spectrum.

        Returns:
            The corrected bin indices.
        """
        return bin_indices

    def _wrap_bin_index(
            self,
            bin_index: np.ndarray | int | float) -> np.ndarray | int | float:
        """Wraps the bin index around.

        Args:
            bin_index: Bin index.

        Returns:
            The bin index after wrapping around.
        """
        return bin_index % self.size


class FftParabolicInterpolationFrequencyEstimator(FftPeakFrequencyEstimator):
    """FFT frequency estimator by identifying the peaks in the FFT spectrum
    and performing a parabolic interpolation.
    """

    def __init__(self, samples: Samples, fs: float, fft_length: int,
                 window: np.ndarray) -> None:
        super().__init__(samples, fs, fft_length, window)

    def _correct_bin_indices(self, bin_indices: np.ndarray) -> np.ndarray:
        """Correct the bin indices corresponding to the peaks in the FFT
        spectrum.

        Args:
            bin_indices: Bin indices corresponding to the peaks in the FFT
              spectrum.

        Returns:
            The corrected bin indices.
        """
        # For each bin index, perform a parabolic interpolation.
        interpolated_bin_indices = np.zeros(bin_indices.shape)
        for index, bin_index in enumerate(bin_indices):
            neighboring_bin_indices = np.array([-1, 0, 1]) + bin_index
            bin_magnitudes = self.get_abs_samples()[self._wrap_bin_index(
                neighboring_bin_indices)]
            parabolic_regression = ParabolicRegression(neighboring_bin_indices,
                                                       bin_magnitudes)
            interpolated_bin_indices[index] = parabolic_regression.peak()[0]
        return interpolated_bin_indices


class FftJacobsenFrequencyEstimator(FftPeakFrequencyEstimator):
    """FFT frequency estimator by identifying the peaks in the FFT spectrum
    and performing a parabolic interpolation.

    See equation (3) of https://ieeexplore.ieee.org/document/4205098.
    """

    def __init__(self, samples: Samples, fs: float, fft_length: int,
                 window: np.ndarray) -> None:
        super().__init__(samples, fs, fft_length, window)

    def _correct_bin_indices(self, bin_indices: np.ndarray) -> np.ndarray:
        """Correct the bin indices corresponding to the peaks in the FFT
        spectrum.

        Args:
            bin_indices: Bin indices corresponding to the peaks in the FFT
              spectrum.

        Returns:
            The corrected bin indices.
        """
        # For each bin index, apply a correction to the spectral peak location.
        corrected_bin_indices = np.zeros(bin_indices.shape)
        for index, bin_index in enumerate(bin_indices):
            neighboring_bin_indices = np.array([-1, 0, 1]) + bin_index
            bin_samples = self.samples[self._wrap_bin_index(
                neighboring_bin_indices)]
            delta = -np.real(
                (bin_samples[2] - bin_samples[0]) /
                (2 * bin_samples[1] - bin_samples[0] - bin_samples[2]))
            corrected_bin_indices[index] = bin_index + delta
        return corrected_bin_indices


class FftWindowedJacobsenFrequencyEstimator(FftPeakFrequencyEstimator):
    """FFT frequency estimator by identifying the peaks in the windowed FFT
    spectrum and performing a parabolic interpolation.

    See equation (5) of https://ieeexplore.ieee.org/document/4205098.
    """

    FFT_WINDOW_TO_CORRECTION_FACTOR = {
        FftWindow.HANN: 0.55,
        FftWindow.HAMMING: 0.60,
        FftWindow.BLACKMAN: 0.55,
    }

    def __init__(self, samples: Samples, fs: float, fft_length: int,
                 window: np.ndarray, window_type: FftWindow) -> None:
        super().__init__(samples, fs, fft_length, window)
        self.window_type = window_type
        if self.window_type not in self.FFT_WINDOW_TO_CORRECTION_FACTOR:
            raise ValueError("Unsupported window type.")

    def _correct_bin_indices(self, bin_indices: np.ndarray) -> np.ndarray:
        """Correct the bin indices corresponding to the peaks in the FFT
        spectrum.

        Args:
            bin_indices: Bin indices corresponding to the peaks in the FFT
              spectrum.

        Returns:
            The corrected bin indices.
        """
        # For each bin index, apply a correction to the spectral peak location.
        corrected_bin_indices = np.zeros(bin_indices.shape)
        for index, bin_index in enumerate(bin_indices):
            neighboring_bin_indices = np.array([-1, 0, 1]) + bin_index
            bin_samples = self.samples[self._wrap_bin_index(
                neighboring_bin_indices)]
            delta = np.real(
                self.FFT_WINDOW_TO_CORRECTION_FACTOR[self.window_type] *
                (bin_samples[0] - bin_samples[2]) /
                (2 * bin_samples[1] + bin_samples[0] + bin_samples[2]))
            corrected_bin_indices[index] = bin_index + delta
        return corrected_bin_indices


class FftTwoPointDtftFrequencyEstimator(FftPeakFrequencyEstimator):
    """FFT frequency estimator by identifying the peaks in the FFT spectrum
    and refining the peak location using the neighboring DTFT coefficients.

    See https://ieeexplore.ieee.org/document/10313215.
    """

    def __init__(self, samples: Samples, fs: float, fft_length: int,
                 window: np.ndarray) -> None:
        super().__init__(samples, fs, fft_length, window)
        self.time_samples = Samples(samples).samples

    def _correct_bin_indices(self, bin_indices: np.ndarray) -> np.ndarray:
        """Correct the bin indices corresponding to the peaks in the FFT
        spectrum.

        Args:
            bin_indices: Bin indices corresponding to the peaks in the FFT
              spectrum.

        Returns:
            The corrected bin indices.
        """
        # For each bin index, perform the refined trick given in Fig. 2 of
        # https://ieeexplore.ieee.org/document/10313215 twice by calculating
        # the magnitude of the DTFT at omega - pi/N and at omega + pi/N and
        # calculating the correction based on the DTFT magnitudes.
        corrected_bin_indices = np.zeros(bin_indices.shape)
        for index, bin_index in enumerate(bin_indices):
            omega_refined = 2 * np.pi / self.size * bin_index
            for _ in range(2):
                omega = omega_refined + np.pi / self.size * np.array([-1, 1])
                # Perform the DTFT at omega - pi/N and at omega + pi/N.
                F = np.exp(-1j * omega[:, np.newaxis] *
                           np.arange(len(self.time_samples)))
                X = F @ self.time_samples
                X_abs = np.abs(X)
                omega_refined = np.mean(omega) + 2 * np.arctan(
                    np.tan(np.diff(omega)[0] / 4) * np.diff(X_abs)[0] /
                    np.sum(X_abs))
            corrected_bin_indices[index] = omega_refined * self.size / (2 *
                                                                        np.pi)
        return corrected_bin_indices
