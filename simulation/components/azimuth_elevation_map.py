"""The azimuth-elevation map performs the direction-of-arrival estimation on the spatial samples."""

import numpy as np

from simulation.components.radar import Radar
from simulation.components.range_doppler_map import RangeDopplerMap
from simulation.components.samples import Samples
from simulation.components.target import Target


class AzimuthElevationMap(Samples):
    """Performs direction-of-arrival estimation on the spatial samples."""

    def __init__(self, samples: Samples, radar: Radar):
        super().__init__(samples)
        self.radar = radar

    def __init__(self, range_doppler_map: RangeDopplerMap, radar: Radar,
                 target: Target):
        range_bin_index, doppler_bin_index = radar.get_range_doppler_bin_indices(
            target)
        spatial_samples = np.zeros(
            (
                np.max(radar.d_tx_ver) + np.max(radar.d_rx_ver),
                np.max(radar.d_tx_hor) + np.max(radar.d_rx_hor),
            ),
            dtype=range_doppler_map.samples.dtype,
        )
        spatial_samples[radar.d_rx_ver,
                        radar.d_rx_hor] = range_doppler_map.samples[
                            range(radar.N_rx), doppler_bin_index,
                            range_bin_index]
        super().__init__(spatial_samples)
        self.radar = radar

    def get_abs_samples(self) -> np.ndarray:
        """Returns the absolute value of the samples."""
        return np.abs(self.samples)

    def perform_azimuth_fft(self) -> None:
        """Performs the FFT in the azimuth dimension."""
        self.samples = np.fft.fft(self.samples, self.radar.N_bins_az, axis=1)

    def perform_elevation_fft(self) -> None:
        """Performs the FFT in the elevation dimension."""
        self.samples = np.fft.fft(self.samples, self.radar.N_bins_el, axis=0)

    def perform_2d_fft(self) -> None:
        """Performs the FFT in the azimuth and elevation dimensions."""
        self.samples = np.fft.fft2(self.samples,
                                   (self.radar.N_bins_el, self.radar.N_bins_az))

    def fft_shift(self) -> None:
        """Performs a FFT shift in the azimuth and elevation dimensions."""
        self.samples = np.fft.fftshift(self.samples)
