"""The chirp processor performs the range processing on the ADC samples."""

import numpy as np

from simulation.radar.components.chirp import ChirpType
from simulation.radar.components.radar import Radar
from simulation.radar.components.samples import Samples
from simulation.radar.processors.fft_processor import FftProcessor1D
from simulation.radar.processors.matched_filter_processor import \
    MatchedFilterProcessor1D
from simulation.radar.processors.signal_processor import SignalProcessor1D


class ChirpProcessor(SignalProcessor1D):
    """Interface for a chirp processor.

    The samples should be one-dimensional.
    """

    def __init__(self, samples: Samples, radar: Radar):
        super().__init__(samples, radar)

    @property
    def title(self) -> str:
        """Title of the spectrum."""
        return "Range processing"

    @property
    def label_axis(self) -> str:
        """Label of the range axis."""
        return "Range in m"

    def get_window(self) -> np.ndarray:
        """Returns the range window."""
        return self.radar.window_r

    def get_output_axis(self) -> np.ndarray:
        """Returns the range axis."""
        return self.radar.r_axis

    @property
    def r_max(self) -> float:
        """Maximum range in m."""
        return self.radar.r_max

    @property
    def r_res(self) -> float:
        """Range resolution in m."""
        return self.radar.r_res


class ChirpFftProcessor(FftProcessor1D, ChirpProcessor):
    """Performs range processing using a 1D FFT."""

    def __init__(self, samples: Samples, radar: Radar):
        super().__init__(samples, radar)


class LinearChirpProcessor(MatchedFilterProcessor1D, ChirpProcessor):
    """Performs range processing on a linear chirp using a matched filter."""

    def __init__(self, samples: Samples, radar: Radar):
        super().__init__(samples, radar)

    def generate_matched_filter(self, value: float) -> np.ndarray:
        """Generates the 1D matched filter against which the samples will be correlated.

        Args:
            value: Range value.

        Returns:
            A 1D matched filter for the given range value.
        """
        r = value
        return np.exp(1j * 2 * np.pi * r / self.r_max *
                      np.arange(self.radar.N_r))


class QuadraticChirpProcessor(MatchedFilterProcessor1D, ChirpProcessor):
    """Performs range processing on a quadratic chirp using a matched filter."""

    def __init__(self, samples: Samples, radar: Radar):
        super().__init__(samples, radar)

    @property
    def r_max(self) -> float:
        """Maximum range in m."""
        return self.radar.c * self.radar.fs / (2 * self.radar.b)

    @property
    def r_res(self) -> float:
        """Range resolution in m."""
        return (
            self.radar.c * self.radar.fs /
            (2 *
             (self.radar.b + self.radar.a * self.radar.Tc) * self.radar.N_r))

    def get_window(self) -> np.ndarray:
        """Returns the window for the samples."""
        n = (np.sqrt(self.radar.a / 2) * np.arange(self.radar.N_r + 2) /
             self.radar.fs + self.radar.b / np.sqrt(2 * self.radar.a))**2
        M = (np.sqrt(self.radar.a / 2) * (self.radar.N_r + 1) / self.radar.fs +
             self.radar.b / np.sqrt(2 * self.radar.a))**2
        window = (0.42 - 0.5 * np.cos(2 * np.pi * n / M) +
                  0.08 * np.cos(4 * np.pi * n / M))[1:-1]
        window /= np.linalg.norm(window)
        return window

    def generate_matched_filter(self, value: float) -> np.ndarray:
        """Generates the 1D matched filter against which the samples will be correlated.

        Args:
            value: Range value.

        Returns:
            A 1D matched filter for the given range value.
        """
        r = value
        tau = 2 * r / self.radar.c
        return np.exp(1j * 2 * np.pi *
                      (self.radar.b * tau * self.radar.t_axis_chirp +
                       1 / 2 * self.radar.a * tau * self.radar.t_axis_chirp**2 -
                       1 / 2 * self.radar.a * tau**2 * self.radar.t_axis_chirp))


class ExponentialChirpProcessor(MatchedFilterProcessor1D, ChirpProcessor):
    """Performs range processing on an exponential chirp using a matched filter."""

    def __init__(self, samples: Samples, radar: Radar):
        super().__init__(samples, radar)

    @property
    def r_max(self) -> float:
        """Maximum range in m."""
        return (self.radar.c / (2 * self.radar.alpha) *
                np.log(1 / (1 - self.radar.fs / self.radar.beta)))

    @property
    def r_res(self) -> float:
        """Range resolution in m."""
        return (self.radar.c / (2 * self.radar.alpha) * np.log(
            1 /
            (1 - self.radar.fs /
             (self.radar.beta * self.radar.N_r *
              np.exp(self.radar.alpha *
                     (self.radar.Tc - 2 * self.radar.r_max / self.radar.c))))))

    def get_window(self) -> np.ndarray:
        """Returns the window for the samples."""
        n = np.exp(self.radar.alpha * np.arange(self.radar.N_r + 2) /
                   self.radar.fs)
        M = np.exp(self.radar.alpha * (self.radar.N_r + 1) / self.radar.fs)
        window = (0.42 - 0.5 * np.cos(2 * np.pi * n / M) +
                  0.08 * np.cos(4 * np.pi * n / M))[1:-1]
        window /= np.linalg.norm(window)
        return window

    def generate_matched_filter(self, value: float) -> np.ndarray:
        """Generates the 1D matched filter against which the samples will be correlated.

        Args:
            value: Range value.

        Returns:
            A 1D matched filter for the given range value.
        """
        r = value
        return np.exp(1j * 2 * np.pi * self.radar.beta / self.radar.alpha *
                      np.exp(self.radar.alpha * self.radar.t_axis_chirp) *
                      (1 - np.exp(-self.radar.alpha * 2 * r / self.radar.c)))


class ChirpMatchedFilterProcessorFactory:
    """Factory for a chirp processor using a matched filter."""

    # Map from chirp type to chirp processor class.
    CHIRP_PROCESSOR_MAP = {
        ChirpType.LINEAR: LinearChirpProcessor,
        ChirpType.QUADRATIC: QuadraticChirpProcessor,
        ChirpType.EXPONENTIAL: ExponentialChirpProcessor,
    }

    @staticmethod
    def create(chirp_type: ChirpType, *args, **kwargs):
        if chirp_type not in ChirpMatchedFilterProcessorFactory.CHIRP_PROCESSOR_MAP:
            raise ValueError(f"Unimplemented chirp type: {chirp_type}.")
        return ChirpMatchedFilterProcessorFactory.CHIRP_PROCESSOR_MAP[
            chirp_type](*args, **kwargs)
