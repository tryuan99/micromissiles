"""The radiation pattern class interpolates the simulated radiation pattern of
an antenna from HFSS.
"""

import numpy as np
import pandas as pd

from simulation.antenna.antenna import Antenna
from utils import constants


class RadiationPattern(Antenna):
    """Radiation pattern.

    The antenna lies in the x-y plane, and its radiation propagates in the +z
    direction. The horizontal axis is parallel to the x-axis, and the vertical
    axis points in the +y direction.

    In HFSS, theta corresponds to the angle measured from the z-axis to the x-y
    plane while phi corresponds to the angle measured counterclockwise from the
    x-axis to the y-axis.

    Attributes:
        df: Dataframe containing the simulated radiation pattern.
        phi_column: Dataframe column corresponding to phi.
        theta_column: Dataframe column corresponding to theta.
        rE_colun: Dataframe column corresponding to the far-field E field
          magnitude.
    """

    def __init__(self, data_csv: str) -> None:
        super().__init__()
        self.df = pd.read_csv(data_csv, comment="#")
        self.phi_column, self.theta_column, self.rE_column = self.df.columns

    def transform_to_cartesian(
            self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Returns the Cartesian coordinates of the data points.

        The x-coordinates, y-coordinates, and z-coordinates are normalized.
        
        Returns:
            A tuple consisting of the x-coordinates, y-coordinates, and
            z-coordinates.
        """
        x = (np.sin(constants.deg2rad(self.df[self.theta_column])) *
             np.cos(constants.deg2rad(self.df[self.phi_column])))
        y = (np.sin(constants.deg2rad(self.df[self.theta_column])) *
             np.sin(constants.deg2rad(self.df[self.phi_column])))
        z = np.cos(constants.deg2rad(self.df[self.theta_column]))
        return x, y, z

    def calculate_pattern(self, azimuth: float | np.ndarray,
                          elevation: float | np.ndarray) -> float | np.ndarray:
        """Calculates the radiation pattern of the antenna.

        Args:
            azimuth: Azimuth in radians.
            elevation: Elevation in radians.

        Returns:
            The magnitude of the radiation pattern.
        """
        # Transform the coordinate systems.
        x = -np.sin(azimuth) * np.cos(elevation)
        y = np.sin(elevation)
        z = np.cos(azimuth) * np.cos(elevation)
        azimuth_pattern = np.arccos(x / np.sqrt(x**2 + y**2))
        azimuth_pattern = np.nan_to_num(azimuth_pattern)
        if isinstance(azimuth_pattern, np.ndarray):
            azimuth_pattern[y < 0] *= -1
        elif y < 0:
            azimuth_pattern *= -1
        elevation_pattern = np.arccos(z)
        return self._calculate_pattern(azimuth_pattern, elevation_pattern)

    def _calculate_pattern(self, azimuth: float | np.ndarray,
                           elevation: float | np.ndarray) -> float | np.ndarray:
        """Calculates the radiation pattern of the antenna.

        Args:
            azimuth: Azimuth in radians.
            elevation: Elevation in radians.

        Returns:
            The magnitude of the radiation pattern.
        """
        # TODO(titan): To be implemented.
        return np.zeros(azimuth.shape)
