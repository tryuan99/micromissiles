"""The isotropic antenna class represents a single isotropic radiator."""

import numpy as np

from simulation.antenna.antenna import Antenna
from simulation.antenna.radiation_pattern import RadiationPattern


class IsotropicAntenna(Antenna):
    """Isotropic antenna."""

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
        shape = np.broadcast_shapes(np.shape(azimuth), np.shape(elevation))
        radiation_pattern = np.ones(shape)
        return RadiationPattern(radiation_pattern, azimuth, elevation)
