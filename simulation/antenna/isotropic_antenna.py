"""The isotropic antenna class represents a single isotropic radiator."""

import numpy as np

from simulation.antenna.antenna import Antenna


class IsotropicAntenna(Antenna):
    """Isotropic antenna."""

    def calculate_pattern(self, azimuth: float | np.ndarray,
                          elevation: float | np.ndarray) -> float | np.ndarray:
        """Calculates the radiation pattern of the antenna.

        Args:
            azimuth: Azimuth in radians.
            elevation: Elevation in radians.

        Returns:
            The magnitude of the radiation pattern.
        """
        shape = np.broadcast_shapes(np.shape(azimuth), np.shape(elevation))
        return np.ones(shape)
