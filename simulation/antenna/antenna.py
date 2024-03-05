"""The antenna class is an interface for all antennas."""

from abc import ABC, abstractmethod

import numpy as np


class Antenna(ABC):
    """Interface for an antenna."""

    @abstractmethod
    def calculate_pattern(self, azimuth: float | np.ndarray,
                          elevation: float | np.ndarray) -> float | np.ndarray:
        """Calculates the radiation pattern of the antenna.

        Args:
            azimuth: Azimuth in radians.
            elevation: Elevation in radians.

        Returns:
            The magnitude of the radiation pattern.
        """
