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
    def get_frequency(self, delay: float = 0) -> np.ndarray | float:
        """Returns the instantaneous frequency of the chirp.

        By definition, the instantaneous frequency is equal to 1/2pi * dphi/dt.

        Args:
            delay: Time delay in seconds.
        """

    def get_phase(self, delay: float = 0) -> np.ndarray | float:
        """Returns the phase of the chirp.

        Args:
            delay: Time delay in seconds.
        """
        return (self.get_unwrapped_phase(delay) + np.pi) % (2 * np.pi) - np.pi

    @abstractmethod
    def get_unwrapped_phase(self, delay: float = 0) -> np.ndarray | float:
        """Returns the unwrapped phase of the chirp.

        Args:
            delay: Time delay in seconds.
        """

    def get_signal(self,
                   delay: float = 0,
                   real: bool = False) -> np.ndarray | float:
        """Returns the complex signal of the chirp.

        Args:
            delay: Time delay in seconds.
            real: If true, returns a real signal instead of a complex signal.
        """
        if real:
            return np.cos(self.get_unwrapped_phase(delay))
        return np.exp(1j * self.get_unwrapped_phase(delay))

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

    def get_frequency(self, delay: float = 0) -> np.ndarray | float:
        """Returns the instantaneous frequency of the chirp.

        By definition, the instantaneous frequency is equal to 1/2pi * dphi/dt.

        Args:
            delay: Time delay in seconds.
        """
        t_axis = self.radar.t_axis_chirp - delay
        return self.radar.f0 + self.radar.mu * t_axis

    def get_unwrapped_phase(self, delay: float = 0) -> np.ndarray | float:
        """Returns the unwrapped phase of the chirp.

        Args:
            delay: Time delay in seconds.
        """
        t_axis = self.radar.t_axis_chirp - delay
        return (2 * np.pi *
                (self.radar.f0 * t_axis + 1 / 2 * self.radar.mu * t_axis**2))

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

    def get_frequency(self, delay: float = 0) -> np.ndarray | float:
        """Returns the instantaneous frequency of the chirp.

        By definition, the instantaneous frequency is equal to 1/2pi * dphi/dt.

        Args:
            delay: Time delay in seconds.
        """
        t_axis = self.radar.t_axis_chirp - delay
        return (self.radar.f0 + self.radar.b * t_axis +
                1 / 2 * self.radar.a * t_axis**2)

    def get_unwrapped_phase(self, delay: float = 0) -> np.ndarray | float:
        """Returns the unwrapped phase of the chirp.

        Args:
            delay: Time delay in seconds.
        """
        t_axis = self.radar.t_axis_chirp - delay
        return (2 * np.pi *
                (self.radar.f0 * t_axis + 1 / 2 * self.radar.b * t_axis**2 +
                 1 / 6 * self.radar.a * t_axis**3))

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

    def get_frequency(self, delay: float = 0) -> np.ndarray | float:
        """Returns the instantaneous frequency of the chirp.

        By definition, the instantaneous frequency is equal to 1/2pi * dphi/dt.

        Args:
            delay: Time delay in seconds.
        """
        t_axis = self.radar.t_axis_chirp - delay
        return (self.radar.f0 + self.radar.beta *
                (np.exp(self.radar.alpha * t_axis) - 1))

    def get_unwrapped_phase(self, delay: float = 0) -> np.ndarray | float:
        """Returns the unwrapped phase of the chirp.

        Args:
            delay: Time delay in seconds.
        """
        t_axis = self.radar.t_axis_chirp - delay
        return (2 * np.pi *
                (self.radar.f0 * t_axis + self.radar.beta / self.radar.alpha *
                 np.exp(self.radar.alpha * t_axis) - self.radar.beta * t_axis))

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


# Map from chirp type to chirp class.
CHIRP_MAP = {
    ChirpType.LINEAR: LinearChirp,
    ChirpType.QUADRATIC: QuadraticChirp,
    ChirpType.EXPONENTIAL: ExponentialChirp,
}
