"""The antenna class is an interface for all antennas."""

from abc import ABC, abstractmethod

import numpy as np

from simulation.antenna.radiation_pattern import RadiationPattern


class Antenna(ABC):
    """Interface for an antenna."""

    @abstractmethod
    def calculate_radiation_pattern(
        self,
        azimuth: float | np.ndarray,
        elevation: float | np.ndarray,
    ) -> RadiationPattern:
        """Calculates the radiation pattern of the antenna.

        Args:
            azimuth: Azimuth in radians.
            elevation: Elevation in radians.

        Returns:
            The power magnitude of the radiation pattern.
        """
