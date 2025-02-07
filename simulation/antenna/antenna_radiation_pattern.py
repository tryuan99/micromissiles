"""The antenna radiation pattern class interpolates the radiation pattern of an
antenna, including the simulated antenna radiation pattern from HFSS.
"""

import numpy as np
import pandas as pd
import scipy.interpolate

from simulation.antenna.antenna import Antenna
from utils import constants
from utils.coordinates import SphericalCoordinates


class AntennaRadiationPattern(Antenna):
    """Antenna radiation pattern.

    The antenna lies in the x-y plane, and its radiation propagates in the +z
    direction. The horizontal axis is parallel to the x-axis, and the vertical
    axis points in the +y direction.

    In HFSS, theta corresponds to the angle measured from the z-axis to the x-y
    plane while phi corresponds to the angle measured counterclockwise from the
    x-axis to the y-axis.

    The dataframe should have three columns in the following order:
        phi: The angle in degrees measured counterclockwise from the x-axis to
          the y-axis.
        theta: The angle in degrees measured from the z-axis to the x-y plane.
        gain: The far-field antenna gain in dB.

    Attributes:
        df: Dataframe containing the radiation pattern.
        phi_column: Dataframe column corresponding to phi.
        theta_column: Dataframe column corresponding to theta.
        gain_column: Dataframe column corresponding to the far-field antenna
          gain on a linear scale.
        gain_db_column: Dataframe column corresponding to the far-field antenna
          gain in dB.
        interpolator: The interpolator of the radiation pattern.
    """

    def __init__(self, data_csv: str) -> None:
        super().__init__()

        self.df = pd.read_csv(data_csv, comment="#")
        (
            self.phi_column,
            self.theta_column,
            self.gain_db_column,
        ) = self.df.columns

        # Convert the gain in dB to a linear scale.
        self.gain_column = "Gain"
        self.df[self.gain_column] = (constants.db2power(
            self.df[self.gain_db_column]))

        # Interpolate the radiation pattern.
        self.interpolator = self._interpolate_pattern()

    def transform_to_cartesian(
            self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Returns the Cartesian coordinates of the data points.

        Returns:
            A tuple consisting of the normalized x-coordinates, y-coordinates,
            and z-coordinates.
        """
        x = (np.sin(constants.deg2rad(self.df[self.theta_column])) *
             np.cos(constants.deg2rad(self.df[self.phi_column])))
        y = (np.sin(constants.deg2rad(self.df[self.theta_column])) *
             np.sin(constants.deg2rad(self.df[self.phi_column])))
        z = np.cos(constants.deg2rad(self.df[self.theta_column]))
        return x, y, z

    def calculate_pattern(
        self,
        azimuth: float | np.ndarray,
        elevation: float | np.ndarray,
    ) -> float | np.ndarray:
        """Calculates the radiation pattern of the antenna.

        Args:
            azimuth: Azimuth in radians.
            elevation: Elevation in radians.

        Returns:
            The magnitude of the radiation pattern.
        """
        # Transform the coordinate systems.
        x, y, z = SphericalCoordinates.transform_to_cartesian_arrays(
            range=1,
            azimuth=azimuth,
            elevation=elevation,
        )
        azimuth_pattern = np.arccos(x / np.sqrt(x**2 + y**2))
        azimuth_pattern = np.nan_to_num(azimuth_pattern)
        if isinstance(azimuth_pattern, np.ndarray):
            azimuth_pattern[y < 0] *= -1
        elif y < 0:
            azimuth_pattern *= -1
        elevation_pattern = np.arccos(z)
        return self.interpolator(
            elevation_pattern,
            azimuth_pattern,
            grid=False,
        )

    def _interpolate_pattern(
            self) -> scipy.interpolate.RectSphereBivariateSpline:
        """Interpolates the radiation pattern of the antenna.

        Returns:
            The interpolator of the radiation pattern.
        """
        df = self.df.copy()

        # Remove duplicate values at theta = -90 degrees.
        df = df[df[self.phi_column] != -90]

        # The interpolator requires data points to have a theta between 0 and
        # 180 degrees and a phi between 0 and 360 degrees, so "flip" the data
        # points with a negative theta.
        flipped_indices = df[self.theta_column] < 0
        df.loc[flipped_indices, self.theta_column] *= -1
        df.loc[flipped_indices, self.phi_column] += 180

        # Mod the thetas to be positive and the phis to be between -180 and 180
        # degrees.
        df[self.theta_column] %= 180
        df.loc[df[self.phi_column] >= 180, self.phi_column] -= 360

        # Filter out the data points at either pole, where theta = 0 or theta
        # = 180 degrees.
        filtered_indices = ((df[self.theta_column] != 0) &
                            (df[self.theta_column] != 180))
        df = df[filtered_indices]

        # Sort the Dataframe in increasing theta.
        df.sort_values(by=[self.theta_column, self.phi_column], inplace=True)

        # Interpolate the radiation pattern over the entire sphere.
        theta = constants.deg2rad(df[self.theta_column].unique())
        phi = constants.deg2rad(df[self.phi_column].unique())
        gain = df[self.gain_column].to_numpy().reshape(len(theta), len(phi))
        return scipy.interpolate.RectSphereBivariateSpline(theta, phi, gain)
