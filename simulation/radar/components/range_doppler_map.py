"""The range-Doppler map performs the range and Doppler processing on the ADC samples."""

import numpy as np

from simulation.radar.components.radar import Radar
from simulation.radar.components.samples import Samples


class RangeDopplerMap(Samples):
    """Performs range and Doppler processing on the ADC samples."""

    def __init__(self, samples: Samples, radar: Radar):
        super().__init__(samples)
        self.radar = radar

    def accumulate_log_magnitude(self) -> np.ndarray:
        """Returns the log magnitude of the samples accumulated over all RX antennas.

        The accumulated range-Doppler map is intended for CFAR.
        """
        # mmWave SDK uses a logarithmic CFAR with a base-2 logarithm.
        return np.sum(np.log2(np.abs(self.samples)), axis=0)

    def apply_range_window(self) -> None:
        """Applies a window in the range dimension."""
        self.samples = np.einsum("kij,j->kij", self.samples,
                                 self.radar.window_r)

    def apply_doppler_window(self) -> None:
        """Applies a window in the Doppler dimension."""
        self.samples = np.einsum("kij,i->kij", self.samples,
                                 self.radar.window_v)

    def apply_2d_window(self) -> None:
        """Applies a window in the range and Doppler dimensions."""
        self.apply_range_window()
        self.apply_doppler_window()

    def perform_range_fft(self) -> None:
        """Performs the FFT in the range dimension."""
        self.samples = np.fft.fft(self.samples, self.radar.N_bins_r, axis=2)

    def perform_doppler_fft(self) -> None:
        """Performs the FFT in the Doppler dimension."""
        self.samples = np.fft.fft(self.samples, self.radar.N_bins_v, axis=1)

    def perform_2d_fft(self) -> None:
        """Performs the FFT in the range and Doppler dimensions."""
        self.samples = np.fft.fft2(self.samples,
                                   (self.radar.N_bins_v, self.radar.N_bins_r))

    def apply_2d_matched_filter(self) -> None:
        """Applies a 2D matched filter in the range and Doppler dimensions.

        The 2D matched filter compensates for range cell migration and for the
        Doppler shift.
        The 2D matched filter is especially useful when v or mu is large.
        """
        matched_filter_out = np.zeros(
            (len(self.samples), self.radar.N_bins_v, self.radar.N_bins_r),
            dtype=np.complex128)
        for v_index, v in enumerate(self.radar.v_axis):
            for r_index, r in enumerate(self.radar.r_axis):
                matched_filter = np.exp(
                    1j * 2 * np.pi * 2 / self.radar.c * np.multiply(
                        r + v * self.radar.t_axis,
                        self.radar.mu * np.repeat(
                            [self.radar.t_axis_chirp], self.radar.N_v, axis=0) +
                        self.radar.f0))
                matched_filter_out[:, v_index, r_index] = np.sum(np.multiply(
                    self.samples, np.conjugate(matched_filter)),
                                                                 axis=(-2, -1))
        self.samples = matched_filter_out

    def fft_shift(self) -> None:
        """Performs a FFT shift in the Doppler dimension."""
        self.samples = np.fft.fftshift(self.samples, axes=1)
