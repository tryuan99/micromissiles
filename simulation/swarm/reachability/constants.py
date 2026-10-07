"""This file defines some useful constants and conversions."""

import casadi
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
_MIN_CLAMPING = 1e-9

# Minimum norm for defining the look rotation.
_MIN_NORM_LOOK_ROTATION = 1e-5

# Speed threshold and angular rate for velocity alignment.
_ALIGNMENT_MIN_SPEED = 0.1
_ALIGNMENT_RATE = np.deg2rad(10000.0)
_MIN_COSINE_COINCIDENT = 1e-12


def gravity_vector() -> np.ndarray:
    """Returns a downward gravity vector in m/s^2 with shape (3,)."""
    return -GRAVITY * UP


def normalize_vector(vector: np.ndarray,
                     fallback: np.ndarray = FORWARD) -> np.ndarray:
    """Returns the normalized vector, or fallback if its magnitude is near zero.

    Args:
        vector: Vector to normalize.
        fallback: Vector returned if the magnitude is near zero.
    """
    magnitude = np.linalg.norm(vector)
    if magnitude < _MIN_CLAMPING:
        return fallback
    return vector / magnitude


def project_onto_axis(vector: np.ndarray, direction: np.ndarray) -> np.ndarray:
    """Returns the component of the vector parallel to the direction vector.

    Args:
        vector: Vector to project.
        direction: Direction vector of the axis.
    """
    return np.dot(vector, direction) / np.linalg.norm(direction)**2 * direction


def normal_basis(normal: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Returns two orthonormal vectors spanning the plane normal to the normal
    vector.

    Args:
        normal: Unit normal vector of the plane.
    """
    reference = UP if abs(np.dot(normal, UP)) < 0.95 else FORWARD
    first_normal_axis = normalize_vector(reference -
                                         project_onto_axis(reference, normal))
    second_normal_axis = np.cross(normal, first_normal_axis)
    return first_normal_axis, second_normal_axis


def casadi_vector_norm(
    vector: casadi.SX | casadi.MX | casadi.DM,
) -> casadi.SX | casadi.MX | casadi.DM:
    """Returns the exact Euclidean norm as a CasADi expression.

    The symbolic derivative is defined as zero on the zero-vector branch.

    Args:
        vector: A CasADi vector whose norm is evaluated.
    """
    squared = casadi.dot(vector, vector)
    root = casadi.sqrt(casadi.if_else(squared > 0, squared, 1))
    return casadi.if_else(squared > 0, root, 0)


def casadi_unit_vector(
    vector: casadi.SX | casadi.MX | casadi.DM,
) -> casadi.SX | casadi.MX | casadi.DM:
    """Returns a normalized CasADi vector or the default forward direction.

    Args:
        vector: A CasADi vector to normalize.
    """
    magnitude = casadi_vector_norm(vector)
    near_zero = magnitude < _MIN_CLAMPING
    return casadi.if_else(
        near_zero,
        casadi.DM(FORWARD),
        vector / casadi.if_else(near_zero, 1, magnitude),
    )


def casadi_project_off_axis(
    vector: casadi.SX | casadi.MX | casadi.DM,
    forward: casadi.SX | casadi.MX | casadi.DM,
) -> casadi.SX | casadi.MX | casadi.DM:
    """Returns the component perpendicular to a CasADi direction vector.

    The direction does not need to have unit magnitude.

    Args:
        vector: A CasADi vector to project.
        forward: A nonzero direction vector defining the projection axis.
    """
    projection = casadi.dot(vector, forward) / casadi.dot(forward, forward)
    return vector - projection * forward


def casadi_clamp_magnitude(
    vector: casadi.SX | casadi.MX | casadi.DM,
    maximum: float | casadi.SX | casadi.MX | casadi.DM,
) -> casadi.SX | casadi.MX | casadi.DM:
    """Returns a CasADi vector limited to a maximum magnitude.

    Args:
        vector: A CasADi vector to limit.
        maximum: A nonnegative scalar magnitude limit.
    """
    magnitude = casadi_vector_norm(vector)
    denominator = casadi.if_else(magnitude > 0, magnitude, 1)
    limited = magnitude > maximum
    return vector * casadi.if_else(limited, maximum / denominator, 1)


def casadi_rotate_vector(
    rotation: casadi.SX | casadi.MX | casadi.DM,
    vector: casadi.SX | casadi.MX | casadi.DM,
) -> casadi.SX | casadi.MX | casadi.DM:
    """Returns a vector rotated by a unit quaternion in xyzw order.

    Args:
        rotation: Unit quaternion with shape (4,).
        vector: Vector with shape (3,).
    """
    crossed = 2 * casadi.cross(rotation[:3], vector)
    return vector + rotation[3] * crossed + casadi.cross(rotation[:3], crossed)


def casadi_look_rotation(
    direction: casadi.SX | casadi.MX | casadi.DM,
) -> casadi.SX | casadi.MX | casadi.DM:
    """Returns a rotation facing the direction with world up.

    Vertical directions use a rotation from the forward axis. A zero
    direction returns the identity rotation.

    Args:
        direction: Forward direction with shape (3,).
    """
    forward = casadi_unit_vector(direction)
    horizontal_length = casadi_vector_norm(
        casadi.vertcat(forward[0], forward[2]))
    has_horizontal_direction = horizontal_length > 0
    yaw_denominator = casadi.if_else(has_horizontal_direction, forward[2], 1)
    yaw = casadi.if_else(has_horizontal_direction,
                         casadi.atan2(forward[0], yaw_denominator), 0)
    pitch = casadi.atan2(-forward[1], horizontal_length)
    half_yaw, half_pitch = yaw / 2, pitch / 2
    rotation = casadi.vertcat(
        casadi.cos(half_yaw) * casadi.sin(half_pitch),
        casadi.sin(half_yaw) * casadi.cos(half_pitch),
        -casadi.sin(half_yaw) * casadi.sin(half_pitch),
        casadi.cos(half_yaw) * casadi.cos(half_pitch))
    return casadi.if_else(
        casadi_vector_norm(direction) > _MIN_NORM_LOOK_ROTATION, rotation,
        casadi.DM([0, 0, 0, 1]))


def casadi_align_rotation(
    rotation: casadi.SX | casadi.MX | casadi.DM,
    velocity: casadi.SX | casadi.MX | casadi.DM,
    time_step: float | casadi.SX | casadi.MX,
) -> casadi.SX | casadi.MX | casadi.DM:
    """Returns the rate-limited alignment toward the current velocity.

    Args:
        rotation: Current unit quaternion in xyzw order.
        velocity: Velocity in m/s with shape (3,).
        time_step: Physics step in seconds.
    """
    target = casadi_look_rotation(velocity)
    cosine = casadi.dot(rotation, target)
    target = casadi.if_else(cosine < 0, -target, target)
    cosine = casadi.fmin(casadi.fabs(cosine), 1)
    coincident = cosine > 1 - _MIN_COSINE_COINCIDENT
    angle = casadi.acos(casadi.if_else(coincident, 0, cosine))
    fraction = casadi.fmin(1, _ALIGNMENT_RATE * time_step / (2 * angle))
    denominator = casadi.sin(angle)
    interpolated = (casadi.sin((1 - fraction) * angle) * rotation +
                    casadi.sin(fraction * angle) * target) / denominator
    aligned = casadi.if_else(coincident, target, interpolated)
    return casadi.if_else(
        casadi_vector_norm(velocity) > _ALIGNMENT_MIN_SPEED, aligned, rotation)
