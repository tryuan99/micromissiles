"""The chirp class represents a single chirp transmitted and received by the radar.
"""

from abc import ABC, abstractmethod
from enum import Enum

import numpy as np

from simulation.radar.components.radar import Radar


class Chirp(ABC):
    """Interface for a single chirp.."""

    def __init__(self, radar: Radar):
        self.radar = radar

    @abstractmethod
    def get_frequency(self) -> np.ndarray | float:
        """Returns the instantaneous frequency of the chirp.

        By definition, the instantaneous frequency is equal to 1/2pi * dphi/dt.
        """

    def get_phase(self) -> np.ndarray | float:
        """Returns the phase of the chirp."""
        return (self.get_unwrapped_phase() + np.pi) % (2 * np.pi) - np.pi

    @abstractmethod
    def get_unwrapped_phase(self) -> np.ndarray | float:
        """Returns the unwrapped phase of the chirp."""

    def get_signal(self, real: bool = False) -> np.ndarray | float:
        """Returns the complex signal of the chirp.

        Args:
            real: If true, returns a real signal instead of a complex signal.
        """
        if real:
            return np.cos(self.get_unwrapped_phase())
        return np.exp(1j * self.get_unwrapped_phase())

    @abstractmethod
    def get_if_frequency(self, tau: np.ndarray | float) -> np.ndarray | float:
        """Returns the instantaneous frequency of the IF of the chirp.

        By definition, the instantaneous frequency is equal to 1/2pi * dphi/dt.

        Args:
            tau: Return time-of-flight for each sample.
        """

    def get_if_phase(self, tau: np.ndarray | float):
        """Returns the phase of the IF of the chirp.

        Args:
            tau: Return time-of-flight for each sample.
        """
        return (self.get_if_unwrapped_phase(tau) + np.pi) % (2 * np.pi) - np.pi

    @abstractmethod
    def get_if_unwrapped_phase(self,
                               tau: np.ndarray | float) -> np.ndarray | float:
        """Returns the unwrapped phase of the IF of the chirp.

        Args:
            tau: Return time-of-flight for each sample.
        """

    def get_if_signal(self,
                      tau: np.ndarray | float,
                      real: bool = False) -> np.ndarray | float:
        """Returns the complex IF signal of the chirp.

        Args:
            tau: Return time-of-flight for each sample.
            real: If true, returns a real signal instead of a complex signal.
        """
        if real:
            return np.cos(self.get_if_unwrapped_phase(tau))
        return np.exp(1j * self.get_if_unwrapped_phase(tau))


class LinearChirp(Chirp):
    """Represents a chirp whose instantaneous frequency increases linearly with time.

    f(t) = f0 + mu*t
    """

    def __init__(self, radar: Radar):
        super().__init__(radar)

    def get_frequency(self) -> np.ndarray | float:
        """Returns the instantaneous frequency of the chirp.

        By definition, the instantaneous frequency is equal to 1/2pi * dphi/dt.
        """
        return self.radar.f0 + self.radar.mu * self.radar.t_axis_chirp

    def get_unwrapped_phase(self) -> np.ndarray | float:
        """Returns the unwrapped phase of the chirp."""
        return (2 * np.pi *
                (self.radar.f0 * self.radar.t_axis_chirp +
                 1 / 2 * self.radar.mu * self.radar.t_axis_chirp**2))

    def get_if_frequency(self, tau: np.ndarray | float) -> np.ndarray | float:
        """Returns the instantaneous frequency of the IF of the chirp.

        By definition, the instantaneous frequency is equal to 1/2pi * dphi/dt.

        Args:
            tau: Return time-of-flight for each sample.
        """
        return self.radar.mu * tau

    def get_if_unwrapped_phase(self,
                               tau: np.ndarray | float) -> np.ndarray | float:
        """Returns the unwrapped phase of the IF of the chirp.

        Args:
            tau: Return time-of-flight for each sample.
        """
        return (2 * np.pi *
                (self.radar.f0 * tau + self.radar.mu * tau *
                 self.radar.t_axis_chirp - 1 / 2 * self.radar.mu * tau**2))


class QuadraticChirp(Chirp):
    """Represents a chirp whose instantaneous frequency increases quadratically with time.

    f(t) = f0 + b*t + 1/2*a*t^2
    """

    def __init__(self, radar: Radar):
        super().__init__(radar)

    def get_frequency(self) -> np.ndarray | float:
        """Returns the instantaneous frequency of the chirp.

        By definition, the instantaneous frequency is equal to 1/2pi * dphi/dt.
        """
        return (self.radar.f0 + self.radar.b * self.radar.t_axis_chirp +
                1 / 2 * self.radar.a * self.radar.t_axis_chirp**2)

    def get_unwrapped_phase(self) -> np.ndarray | float:
        """Returns the unwrapped phase of the chirp."""
        return (2 * np.pi * (self.radar.f0 * self.radar.t_axis_chirp +
                             1 / 2 * self.radar.b * self.radar.t_axis_chirp**2 +
                             1 / 6 * self.radar.a * self.radar.t_axis_chirp**3))

    def get_if_frequency(self, tau: np.ndarray | float) -> np.ndarray | float:
        """Returns the instantaneous frequency of the IF of the chirp.

        By definition, the instantaneous frequency is equal to 1/2pi * dphi/dt.

        Args:
            tau: Return time-of-flight for each sample.
        """
        return (self.radar.b * tau +
                self.radar.a * tau * self.radar.t_axis_chirp -
                1 / 2 * self.radar.a * tau**2)

    def get_if_unwrapped_phase(self,
                               tau: np.ndarray | float) -> np.ndarray | float:
        """Returns the unwrapped phase of the IF of the chirp.

        Args:
            tau: Return time-of-flight for each sample.
        """
        return (2 * np.pi *
                (self.radar.f0 * tau +
                 self.radar.b * tau * self.radar.t_axis_chirp +
                 1 / 2 * self.radar.a * tau * self.radar.t_axis_chirp**2 -
                 1 / 2 * self.radar.b * tau**2 - 1 / 2 * self.radar.a * tau**2 *
                 self.radar.t_axis_chirp + 1 / 6 * self.radar.a * tau**3))


class ExponentialChirp(Chirp):
    """Represents a chirp whose instantaneous frequency increases exponentially with time.

    f(t) = f0 + beta * (e^(alpha*t) - 1)
    """

    def __init__(self, radar: Radar):
        super().__init__(radar)

    def get_frequency(self) -> np.ndarray | float:
        """Returns the instantaneous frequency of the chirp.

        By definition, the instantaneous frequency is equal to 1/2pi * dphi/dt.
        """
        return (self.radar.f0 + self.radar.beta *
                (np.exp(self.radar.alpha * self.radar.t_axis_chirp) - 1))

    def get_unwrapped_phase(self) -> np.ndarray | float:
        """Returns the unwrapped phase of the chirp."""
        return (2 * np.pi *
                (self.radar.f0 * self.radar.t_axis_chirp +
                 self.radar.beta / self.radar.alpha *
                 np.exp(self.radar.alpha * self.radar.t_axis_chirp) -
                 self.radar.beta * self.radar.t_axis_chirp))

    def get_if_frequency(self, tau: np.ndarray | float) -> np.ndarray | float:
        """Returns the instantaneous frequency of the IF of the chirp.

        By definition, the instantaneous frequency is equal to 1/2pi * dphi/dt.

        Args:
            tau: Return time-of-flight for each sample.
        """
        return (self.radar.beta *
                np.exp(self.radar.alpha * self.radar.t_axis_chirp) *
                (1 - np.exp(-self.radar.alpha * tau)))

    def get_if_unwrapped_phase(self,
                               tau: np.ndarray | float) -> np.ndarray | float:
        """Returns the unwrapped phase of the IF of the chirp.

        Args:
            tau: Return time-of-flight for each sample.
        """
        return (2 * np.pi *
                ((self.radar.f0 - self.radar.beta) * tau +
                 self.radar.beta / self.radar.alpha *
                 np.exp(self.radar.alpha * self.radar.t_axis_chirp) *
                 (1 - np.exp(-self.radar.alpha * tau))))


# Chirp type enum.
class ChirpType(str, Enum):
    LINEAR = "linear"
    QUADRATIC = "quadratic"
    EXPONENTIAL = "exponential"

    @classmethod
    def values(cls):
        """Returns a list of all enum values."""
        return list(cls._value2member_map_.keys())


# Map from chirp type to chirp clas.
CHIRP_MAP = {
    ChirpType.LINEAR: LinearChirp,
    ChirpType.QUADRATIC: QuadraticChirp,
    ChirpType.EXPONENTIAL: ExponentialChirp,
}
