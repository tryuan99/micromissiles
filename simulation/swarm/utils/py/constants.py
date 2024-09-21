"""This file defines some useful constants and conversions."""

import numpy as np
import scipy.constants

# Air density in kg/m^3.
AIR_DENSITY = 1.204

# Air density scale height in km.
AIR_DENSITY_SCALE_HEIGHT = 10.4


def air_density_at_altitude(altitude: float | np.ndarray) -> float | np.ndarray:
    """Returns the air density at the given altitude.

    Args:
        altitude: Altitude in meters.

    Returns:
        The air density at the given altitude in kg/m^3.
    """
    return AIR_DENSITY * np.exp(-altitude / (AIR_DENSITY_SCALE_HEIGHT * 1000))


# Standard gravity in m/s^2.
STANDARD_GRAVITY = scipy.constants.g

# Earth's mean radius in meters.
EARTH_MEAN_RADIUS = 6378137


def gravity_at_altitude(altitude: float | np.ndarray) -> float | np.ndarray:
    """Returns the gravitational acceleration at the given altitude.

    Args:
        altitude: Altitude in meters.

    Returns:
        The gravitational acceleration at the given altitude in m/s^2.
    """
    return (STANDARD_GRAVITY * (EARTH_MEAN_RADIUS /
                                (EARTH_MEAN_RADIUS + altitude))**2)
