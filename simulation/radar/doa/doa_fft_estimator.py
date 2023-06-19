"""The direction-of-arrival FFT estimator performs direction-of-arrival
estimation by performing a 2D FFT on the spatial samples.
"""

import numpy as np

from simulation.radar.components.radar import Radar
from simulation.radar.components.spatial_samples import SpatialSamples
from simulation.radar.doa.doa_estimator import DoaEstimator


class DoaFftEstimator(DoaEstimator):
    """Performs direction-of-arrival estimation using a 2D FFT."""

    def __init__(self, radar: Radar, spatial_samples: SpatialSamples):
        super().__init__(radar, spatial_samples)

    def process_spatial_samples(self) -> None:
        """Processes the spatial samples by performing a 2D FFT."""
        self._perform_2d_fft()
        self._fft_shift()

    def estimate_doa(self) -> tuple[float, float]:
        """Estimates the direction-of-arrival.

        Returns:
            A tuple consisting of the estimated (elevation, azimuth) in rad.
        """
        elevation_bin_index, azimuth_bin_index = np.unravel_index(
            np.argmax(self.samples.get_abs_samples()), self.samples.shape)
        return self.radar.el_axis[elevation_bin_index], self.radar.az_axis[
            azimuth_bin_index]

    def _perform_azimuth_fft(self) -> None:
        """Performs the FFT in the azimuth dimension."""
        # The FFT outputs a positive spatial frequency if the phase increases
        # in the positive x-direction. In our coordinate system, the phase
        # increases in the positive x-direction.
        self.samples.samples = np.fft.fft(self.samples.samples,
                                          self.radar.N_bins_az,
                                          axis=1)

    def _perform_elevation_fft(self) -> None:
        """Performs the FFT in the elevation dimension."""
        # The FFT outputs a positive spatial frequency if the phase increases
        # in the positive y-direction. In our coordinate system, the phase
        # increases in the negative y-direction.
        self.samples.samples = np.fft.fft(self.samples.samples,
                                          self.radar.N_bins_el,
                                          axis=0)
        self.samples.samples = np.flip(self.samples.samples, axis=0)

    def _perform_2d_fft(self) -> None:
        """Performs the FFT in the azimuth and elevation dimensions."""
        self.samples.samples = np.fft.fft2(
            self.samples.samples, (self.radar.N_bins_el, self.radar.N_bins_az))
        self.samples.samples = np.flip(self.samples.samples, axis=0)

    def _fft_shift(self) -> None:
        """Performs an FFT shift in the azimuth and elevation dimensions."""
        self.samples.samples = np.fft.fftshift(self.samples.samples)
