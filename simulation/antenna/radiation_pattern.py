"""The radiation pattern represents the radiation pattern of an antenna or
antenna array.
"""

import numpy as np

from utils import constants


class RadiationPattern:
    """Radiation pattern.

    The radiation pattern is assumed in the far field of the antenna and is
    measured in units of power.

    Attributes:
        azimuth: Azimuth in radians.
        elevation: Elevation in radians.
        radiation_pattern: Radiation pattern.
    """

    def __init__(
        self,
        radiation_pattern: np.ndarray,
        azimuth: np.ndarray,
        elevation: np.ndarray,
    ) -> None:
        shape = np.shape(radiation_pattern)
        self.radiation_pattern = radiation_pattern
        self.azimuth = np.broadcast_to(azimuth, shape)
        self.elevation = np.broadcast_to(elevation, shape)

    def db(self, log_plus_one: bool = True) -> np.ndarray:
        """Returns the radiation pattern in dB.

        Args:
            log_plus_one: If true, add 1 prior to taking the logarithm to
              handle any zero values.
        """
        if log_plus_one:
            return constants.power2db(self.radiation_pattern + 1)
        return constants.power2db(self.radiation_pattern)

    def normalized_db(self, log_plus_one: bool = True) -> np.ndarray:
        """Returns the normalized radiation pattern in dB.

        Args:
            log_plus_one: If true, add 1 prior to taking the logarithm to
              handle any zero values.
        """
        return self.db(log_plus_one) - self.max_db(log_plus_one)

    def max(self) -> np.ndarray:
        """Returns the maximum power magnitude in the radiation pattern."""
        return np.max(self.radiation_pattern)

    def max_db(self, log_plus_one: bool = True) -> np.ndarray:
        """Returns the maximum power magnitude in dB in the radiation pattern.

        Args:
            log_plus_one: If true, add 1 prior to taking the logarithm to
              handle any zero values.
        """
        if log_plus_one:
            return constants.power2db(self.max() + 1)
        return constants.power2db(self.max())

    def min(self) -> np.ndarray:
        """Returns the minimum power magnitude in the radiation pattern."""
        return np.min(self.radiation_pattern)

    def min_db(self, log_plus_one: bool = True) -> np.ndarray:
        """Returns the minimum power magnitude in dB in the radiation pattern.

        Args:
            log_plus_one: If true, add 1 prior to taking the logarithm to
              handle any zero values.
        """
        if log_plus_one:
            return constants.power2db(self.min() + 1)
        return constants.power2db(self.min() + 1)
