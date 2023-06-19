"""The direction-of-arrival FFT estimator performs direction-of-arrival
estimation by performing virtual array extension followed by a 2D FFT on the
spatial samples.

See https://www.mdpi.com/1424-8220/18/5/1560 for the paper.
"""

import numpy as np

from simulation.radar.components.radar import Radar
from simulation.radar.components.spatial_samples import SpatialSamples
from simulation.radar.doa.doa_fft_estimator import DoaFftEstimator


class DoaArrayExtensionEstimator(DoaFftEstimator):
    """Performs direction-of-arrival estimation by extending the virtual array
    and performing a 2D FFT.
    """

    def __init__(self, radar: Radar, spatial_samples: SpatialSamples):
        super().__init__(radar, spatial_samples)

    def process_spatial_samples(self) -> None:
        """Processes the spatial samples by performing a 2D FFT."""
        self._perform_virtual_array_extension()
        self._perform_2d_fft()
        self._fft_shift()

    def _perform_virtual_array_extension(self) -> None:
        """Extends the virtual array using simple multiplication.

        u_k = y_0 * y_k for 0 <= k <= K - 1
        u_k = y_{K - 1} * y_{k - K + 1} for K <= k <= 2K - 1
        """
        num_elevation_antennas, num_azimuth_antennas = self.shape
        extended_spatial_samples = np.zeros(2 * np.array(self.shape) - 1,
                                            dtype=self.samples.dtype)

        # Extend in the azimuth dimension.
        extended_spatial_samples[:num_elevation_antennas, :
                                 num_azimuth_antennas] = (
                                     self.samples[:num_elevation_antennas,
                                                  0][:, np.newaxis] *
                                     self.samples[:num_elevation_antennas])
        extended_spatial_samples[:num_elevation_antennas,
                                 num_azimuth_antennas:] = (
                                     self.samples[:num_elevation_antennas,
                                                  num_azimuth_antennas -
                                                  1][:, np.newaxis] *
                                     self.samples[:num_elevation_antennas, 1:])

        # Extend in the elevation dimension.
        extended_azimuth_spatial_samples = (
            extended_spatial_samples[:num_elevation_antennas].copy())
        extended_spatial_samples[:num_elevation_antennas] = (
            extended_azimuth_spatial_samples *
            extended_azimuth_spatial_samples[0])
        extended_spatial_samples[num_elevation_antennas:] = (
            extended_azimuth_spatial_samples[1:] *
            extended_azimuth_spatial_samples[num_elevation_antennas - 1])
