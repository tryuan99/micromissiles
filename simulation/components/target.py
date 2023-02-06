"""The target class represents a single radar target."""

import numpy as np

from simulation.components.coordinates import PolarCoordinates


class Target:
    """Represents a single target.

    The range is the distance from the origin to the target, and the range rate
    is the target's velocity away from the origin.
        range = sqrt(x^2 + y^2 + z^2)
        range_rate = drange / dt
    """

    def __init__(
        self,
        range: float = 0,
        range_rate: float = 0,
        acceleration: float = 0,
        azimuth: float = 0,
        elevation: float = 0,
        rcs: float = 0,
    ):
        self.range = range  # Range in m.
        self.range_rate = range_rate  # Range rate in m/s.
        self.acceleration = acceleration  # Acceleration in m/s^2.
        self.azimuth = azimuth  # Azimuth in radians.
        self.elevation = elevation  # Elevation in radians.
        self.rcs = rcs  # Radar cross section in dBsm.

    def get_distance_over_time(self, t_axis: np.ndarray) -> np.ndarray:
        """Returns the distance of the target along the given time axis.

        Args:
            t_axis: Time axis.
        """
        return (self.range + t_axis * self.range_rate +
                1 / 2 * self.acceleration * t_axis**2)

    def get_position_over_time(self, t_axis: np.ndarray) -> np.ndarray:
        """Returns the position of the target along the given time axis.

        Args:
            t_axis: Time axis.

        Returns:
            (x, y, z), where x, y, and z correspond to the x, y, and z-positions
            of the target along the given time axis.
        """
        d = self.get_distance_over_time(
            t_axis)  # Distance from the origin at each sample in m.
        coordinates = PolarCoordinates(d, self.azimuth, self.elevation)
        return coordinates.transform_to_cartesian().coordinates
