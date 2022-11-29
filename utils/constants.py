"""Constants and related utility functions."""

import numpy as np
from typing import Any


def power2db(power: Any) -> Any:
    """Converts power to dB."""
    return 10 * np.log10(power)


def db2power(db: Any) -> Any:
    """Converts dB to power."""
    return 10 ** (db / 10)


def mag2db(magnitude: Any) -> Any:
    """Converts magnitude, or voltage, to dB."""
    return 20 * np.log10(magnitude)


def db2mag(db: Any) -> Any:
    """Converts dB to magnitude, or voltage."""
    return 10 ** (db / 20)


def power2mag(power: Any) -> Any:
    """Converts power to magnitude using V = sqrt(P * 50 ohms)."""
    return np.sqrt(power * 50)


def mag2power(magnitude: Any) -> Any:
    """Converts magnitude to power using P = V^2 / 50 ohms."""
    return magnitude**2 / 50
