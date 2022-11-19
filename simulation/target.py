"""The target class represents a single radar target."""

import numpy as np


class Target:
    """Represents a single target.

    The target is in the positive z-direction.
    The antennas are positioned in the x-y plane at z=0, where "horizontal"
    denotes the x-direction and "vertical" denotes the y-direction.
    The range is the distance from the origin to the target, and the range rate
    is the target's velocity away from the origin.
        range = sqrt(x^2 + y^2 + z^2)
    We use spherical coordinates for the azimuth and elevation.
    The azimuth denotes the angle from the projection of the target on the x-z
    plane to the z-axis.
        azimuth = arctan(x / z)
    The elevation denotes the angle from the target to its projection on the
    x-z plane.
        elevation = arctan(y / sqrt(x^2 + z^2))
    Converting to Cartesian coordinates:
        x = tan(azimuth) * z
        y = tan(elevation) * sqrt(x^2 + z^2)
        z = r * cos(azimuth) * cos(elevation)
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
        return (
            self.range
            + t_axis * self.range_rate
            + 1 / 2 * self.acceleration * t_axis**2
        )

    def get_position_over_time(self, t_axis: np.ndarray) -> np.ndarray:
        """Returns the position of the target along the given time axis.

        Args:
            t_axis: Time axis.

        Returns:
            (x, y, z), where x, y, and z correspond to the x, y, and z-positions
            of the target along the given time axis.
        """
        d = self.get_distance_over_time(
            t_axis
        )  # Distance from the origin at each sample in m.
        z = (
            d * np.cos(self.azimuth) * np.cos(self.elevation)
        )  # Distance along the z-axis in m.
        x = np.tan(self.azimuth) * z  # Distance along the x-axis in m.
        y = np.tan(self.elevation) * np.sqrt(
            x**2 + z**2
        )  # Distance along the y-axis in m.
        return x, y, z
