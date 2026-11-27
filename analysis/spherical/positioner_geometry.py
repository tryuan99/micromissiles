"""Yaw-over-roll positioner geometry for spherical near-field measurements.

The test antenna is on a roll positioner (around its boresight) mounted on a yaw
positioner (around the vertical). The fixed probe faces the test antenna.

The chamber coordinate system has its origin at the intersection of the axes,
with the +z-axis pointing from the test antenna toward the probe and the +y-axis
pointing up. It coincides with the test antenna coordinate system at zero yaw
and roll.

For right-hand yaw around the +y-axis, right-hand roll around the boresight, and
a probe polarization angle from the +y-axis that is right-handed around the
+z-axis, the Euler angles of the probe (Appendix A2 of J. E. Hansen (ed.),
"Spherical Near-Field Antenna Measurements", 1988) are
    theta = yaw,
    phi = pi - roll,
    chi = probe polarization angle - pi / 2.

The Keysight CATR uses left-hand yaw and roll.
"""

from enum import IntEnum

import numpy as np


class RotationDirection(IntEnum):
    """Sign of a positive positioner angle relative to a right-hand rotation."""
    RIGHT_HAND = 1
    LEFT_HAND = -1


class PositionerGeometry:
    """Converts the positioner angles into the Euler angles of the probe.

    Attributes:
        yaw_direction: Direction of positive yaw.
        roll_direction: Direction of positive roll.
    """

    def __init__(
        self,
        yaw_direction: RotationDirection,
        roll_direction: RotationDirection,
    ) -> None:
        """Initializes the positioner geometry.

        Args:
            yaw_direction: Direction of positive yaw.
            roll_direction: Direction of positive roll.
        """
        self.yaw_direction = yaw_direction
        self.roll_direction = roll_direction

    @staticmethod
    def probe_chi(probe_angle: float) -> float:
        """Converts the probe polarization angle into chi.

        Args:
            probe_angle: Probe polarization angle from vertical in radians.

        Returns:
            Chi in radians for a nonnegative yaw.
        """
        return probe_angle - np.pi / 2

    def spherical_angles(
        self,
        yaws: np.ndarray,
        rolls: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Computes theta and phi of the probe for every yaw and roll.

        A negative yaw is mapped onto a positive theta, which also changes chi
        to chi - pi. Rotating a first-order probe by pi negates the received
        signal, so the sign accounts for the change in chi.

        Args:
            yaws: Yaw angles in radians with shape (num_yaws,).
            rolls: Roll angles in radians with shape (num_rolls,).

        Returns:
            Theta with shape (num_yaws,), phi with shape (num_yaws, num_rolls),
            and the sign of the received signal with shape (num_yaws,).
        """
        theta = self.yaw_direction * np.asarray(yaws, dtype=np.float64)
        phi = np.pi - self.roll_direction * np.asarray(rolls, dtype=np.float64)
        phi = np.broadcast_to(phi, (len(theta), len(phi))).copy()

        # R_y(-theta) = R_z(pi) R_y(theta) R_z(-pi).
        negative = theta < 0
        theta[negative] *= -1
        phi[negative] += np.pi
        return theta, np.mod(phi, 2 * np.pi), np.where(negative, -1, 1)
