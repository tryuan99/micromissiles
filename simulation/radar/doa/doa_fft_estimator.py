"""The direction-of-arrival FFT estimator performs direction-of-arrival
estimation by performing a 2D FFT on the spatial samples.
"""

import numpy as np

from simulation.radar.components.radar import Radar
from simulation.radar.components.spatial_samples import SpatialSamples
from simulation.radar.doa.doa_estimator import DoaEstimator
from simulation.radar.processors.fft_processor import FftProcessor


class DoaFftEstimator(DoaEstimator, FftProcessor):
    """Performs direction-of-arrival estimation using a 2D FFT."""

    def __init__(self, spatial_samples: SpatialSamples, radar: Radar):
        super().__init__(spatial_samples, radar)

    def process_2d_samples(self) -> None:
        """Processes the 2D spatial samples."""
        # For elevation, the FFT outputs a positive spatial frequency if the
        # phase increases in the positive y-direction. In our coordinate system,
        # the phase increases in the negative y-direction.
        #
        # For the azimuth, the FFT outputs a positive spatial frequency if the
        # phase increases in the positive x-direction. In our coordinate system,
        # the phase increases in the positive x-direction.
        self.apply_2d_fft()
        # Flip the values along the elevation dimension.
        self.samples = np.flip(self.samples, axis=-2)
        # Perform an FFT shift in the elevation and azimuth dimensions.
        self.fft_shift_2d()
