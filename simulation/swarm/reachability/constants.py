"""This file defines some useful constants and conversions."""

import numpy as np
import scipy.constants

# Gravity in m/s^2.
GRAVITY = scipy.constants.g

# Air density in kg/m^3.
AIR_DENSITY_SEA_LEVEL = 1.204

# Air density scale height in m.
AIR_DENSITY_SCALE_HEIGHT = 10.4e3

# Default up and forward axes.
UP = np.array([0.0, 1.0, 0.0])
FORWARD = np.array([0.0, 0.0, 1.0])

# Look-ahead time against ground impact in seconds.
GROUND_PROXIMITY_THRESHOLD_FACTOR = 5.0

# Speed error deadband in m/s.
SPEED_ERROR_THRESHOLD = 1.0

# Minimum magnitude for clamping.
_EPSILON = 1e-9


def air_density_at_altitude(altitude: float | np.ndarray) -> float | np.ndarray:
    """Returns the air density at the given altitude.

    Args:
        altitude: Altitude in meters.

    Returns:
        The air density at the given altitude in kg/m^3.
    """
    return AIR_DENSITY_SEA_LEVEL * np.exp(-altitude /
                                          (AIR_DENSITY_SCALE_HEIGHT))


def gravity_vector() -> np.ndarray:
    """Returns the gravity acceleration vector in m/s^2."""
    return -GRAVITY * UP


def normalize_vector(vector: np.ndarray,
                     fallback: np.ndarray = FORWARD) -> np.ndarray:
    """Returns the normalized vector, or fallback if its magnitude is near zero.

    Args:
        vector: Vector to normalize.
        fallback: Vector returned if the magnitude is near zero.
    """
    magnitude = np.linalg.norm(vector)
    if magnitude < _EPSILON:
        return fallback
    return vector / magnitude


def project_onto_axis(vector: np.ndarray, direction: np.ndarray) -> np.ndarray:
    """Returns the component of the vector parallel to the direction vector.

    Args:
        vector: Vector to project.
        direction: Direction vector of the axis.
    """
    return np.dot(vector, direction) / np.linalg.norm(direction)**2 * direction


def project_off_axis(vector: np.ndarray, direction: np.ndarray) -> np.ndarray:
    """Returns the component of the vector perpendicular to the direction vector.

    Args:
        vector: Vector to project.
        direction: Direction vector of the axis.
    """
    return vector - project_onto_axis(vector, direction)


def clamp_magnitude(vector: np.ndarray, maximum_magnitude: float) -> np.ndarray:
    """Returns the vector scaled down to at most the maximum_magnitude.

    Args:
        vector: Vector to clamp.
        maximum_magnitude: Maximum magnitude.
    """
    magnitude = np.linalg.norm(vector)
    if magnitude > maximum_magnitude and magnitude > _EPSILON:
        return vector * (maximum_magnitude / magnitude)
    return vector


def normal_basis(normal: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Returns two orthonormal vectors spanning the plane normal to the normal vector.

    Args:
        normal: Unit normal vector of the plane.
    """
    reference = UP if abs(np.dot(normal, UP)) < 0.95 else FORWARD
    first_normal_axis = normalize_vector(reference -
                                         project_onto_axis(reference, normal))
    second_normal_axis = np.cross(normal, first_normal_axis)
    return first_normal_axis, second_normal_axis
