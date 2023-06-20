"""The direction-of-arrival estimator estimates the azimuth and elevation of
the target relative to the radar's boresight.

The direction-of-arrival estimator takes in spatial samples as its input and
processes them to perform direction-of-arrival estimation.
"""

import numpy as np

from simulation.radar.components.radar import Radar
from simulation.radar.components.samples import Samples
from simulation.radar.processors.signal_processor import SignalProcessor


class DoaEstimator(SignalProcessor):
    """Interface for a direction-of-arrival estimator.

    The first dimension is elevation, and the second dimension is azimuth.
    """

    def __init__(self, samples: Samples, radar: Radar):
        super().__init__(samples, radar)

    @property
    def title(self) -> str:
        """Returns the title of the 2D spectrum."""
        return "Azimuth-elevation spectrum"

    @property
    def label_axis1(self) -> str:
        """Returns the label of the elevation axis."""
        return "Elevation in rad"

    @property
    def label_axis2(self) -> str:
        """Returns the label of the azimuth axis."""
        return "Azimuth in rad"

    def get_window_axis1(self) -> np.ndarray:
        """Returns the elevation window."""
        return np.ones(self.sample.shape[-2])

    def get_window_axis2(self) -> np.ndarray:
        """Returns the azimuth window."""
        return np.ones(self.sample.shape[-1])

    def get_output_axis1(self) -> np.ndarray:
        """Returns the elevation axis."""
        return self.radar.el_axis

    def get_output_axis2(self) -> np.ndarray:
        """Returns the azimuth axis."""
        return self.radar.az_axis
