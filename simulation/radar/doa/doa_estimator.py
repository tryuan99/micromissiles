"""The direction-of-arrival estimator estimates the azimuth and elevation of
the target relative to the radar's boresight.

The direction-of-arrival estimator takes in spatial samples as its input.
"""

from abc import ABC, abstractmethod

import matplotlib.pyplot as plt
import numpy as np

from simulation.radar.components.radar import Radar
from simulation.radar.components.samples import Samples
from utils import constants
from utils.visualization.color_maps import COLOR_MAPS


class DoaEstimator(ABC):
    """Interface for direction-of-arrival estimators."""

    def __init__(self, radar: Radar, samples: Samples):
        self.radar = radar
        self.samples = samples

    @abstractmethod
    def process_spatial_samples(self) -> None:
        """Performs direction-of-arrival estimation by processing the spatial
        samples.
        """

    @abstractmethod
    def estimate_doa(self) -> tuple[float, float]:
        """Estimates the direction-of-arrival.

        Returns:
            A tuple consisting of the estimated (elevation, azimuth) in rad.
        """

    def plot_2d_spectrum(self) -> None:
        """Plots the azimuth-elevation spectrum."""
        fig = plt.figure(figsize=(12, 8))
        ax = plt.axes(projection="3d")
        surf = ax.plot_surface(
            *np.meshgrid(self.radar.el_axis, self.radar.az_axis),
            constants.mag2db(self.samples.get_abs_samples()).T,
            cmap=COLOR_MAPS["parula"],
            antialiased=False,
        )
        ax.set_title("Azimuth-elevation spectrum")
        ax.set_xlabel("Elevation in rad")
        ax.set_ylabel("Azimuth in rad")
        ax.view_init(45, -45)
        plt.colorbar(surf)
        plt.show()
