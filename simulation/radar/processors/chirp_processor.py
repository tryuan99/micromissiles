"""The chirp processor performs the range processing on the ADC samples."""

from abc import abstractmethod

import numpy as np

from simulation.radar.components.chirp import ChirpType
from simulation.radar.components.radar import Radar
from simulation.radar.components.samples import Samples
from simulation.radar.processors.fft_processor import FftProcessor1D
from simulation.radar.processors.matched_filter_processor import \
    MatchedFilterProcessor1D
from simulation.radar.processors.signal_processor import SignalProcessor1D
from simulation.radar.processors.sparse_processor import SparseProcessor1D


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
    @abstractmethod
    def r_max(self) -> float:
        """Maximum range in m."""

    @property
    @abstractmethod
    def r_res(self) -> float:
        """Range resolution in m."""


class ChirpFftProcessor(FftProcessor1D, ChirpProcessor):
    """Interface for a chirp processor using a 1D FFT."""

    def __init__(self, samples: Samples, radar: Radar):
        super().__init__(samples, radar)


class ChirpMatchedFilterProcessor(MatchedFilterProcessor1D, ChirpProcessor):
    """Interface for a chirp processor using a matched filter."""

    def __init__(self, samples: Samples, radar: Radar):
        super().__init__(samples, radar)


class SparseChirpProcessor(SparseProcessor1D, ChirpProcessor):
    """Interface for a chirp processor using compressed sensing."""

    def __init__(self, samples: Samples, radar: Radar):
        super().__init__(samples, radar)


class LinearChirpProcessor(ChirpProcessor):
    """Interface for a linear chirp processor."""

    def __init__(self, samples: Samples, radar: Radar):
        super().__init__(samples, radar)

    @property
    def r_max(self) -> float:
        """Maximum range in m."""
        return self.radar.r_max

    @property
    def r_res(self) -> float:
        """Range resolution in m."""
        return self.radar.r_res


class QuadraticChirpProcessor(ChirpProcessor):
    """Interface for a quadratic chirp processor."""

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


class ExponentialChirpProcessor(ChirpProcessor):
    """Interface for an exponential chirp processor."""

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


class LinearChirpFftProcessor(ChirpFftProcessor, LinearChirpProcessor):
    """Performs range processing on a linear chirp using a 1D FFT."""

    def __init__(self, samples: Samples, radar: Radar):
        super().__init__(samples, radar)


class LinearChirpMatchedFilterProcessor(ChirpMatchedFilterProcessor,
                                        LinearChirpProcessor):
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


class LinearSparseChirpProcessor(SparseChirpProcessor, LinearChirpProcessor):
    """Performs range processing on a linear chirp using compressed sensing."""

    def __init__(self, samples: Samples, radar: Radar):
        super().__init__(samples, radar)

    def generate_sensing_matrix(self) -> np.ndarray:
        """Generates the sensing matrix mapping the sources to the observations.

        The dimensions of the sensing matrix should be (number of sources) x
        (number of samples).

        Returns:
            The sensing matrix.
        """
        r = self.get_output_axis()[:, np.newaxis]
        return np.exp(1j * 2 * np.pi * r / self.r_max *
                      np.arange(self.radar.N_r))


class QuadraticChirpMatchedFilterProcessor(ChirpMatchedFilterProcessor,
                                           QuadraticChirpProcessor):
    """Performs range processing on a quadratic chirp using a matched filter."""

    def __init__(self, samples: Samples, radar: Radar):
        super().__init__(samples, radar)

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


class QuadraticSparseChirpProcessor(SparseChirpProcessor,
                                    QuadraticChirpProcessor):
    """Performs range processing on a quadratic chirp using compressed sensing."""

    def __init__(self, samples: Samples, radar: Radar):
        super().__init__(samples, radar)

    def generate_sensing_matrix(self) -> np.ndarray:
        """Generates the sensing matrix mapping the sources to the observations.

        The dimensions of the sensing matrix should be (number of sources) x
        (number of samples).

        Returns:
            The sensing matrix.
        """
        r = self.get_output_axis()[:, np.newaxis]
        tau = 2 * r / self.radar.c
        return np.exp(1j * 2 * np.pi *
                      (self.radar.b * tau * self.radar.t_axis_chirp +
                       1 / 2 * self.radar.a * tau * self.radar.t_axis_chirp**2 -
                       1 / 2 * self.radar.a * tau**2 * self.radar.t_axis_chirp))


class ExponentialChirpMatchedFilterProcessor(ChirpMatchedFilterProcessor,
                                             ExponentialChirpProcessor):
    """Performs range processing on an exponential chirp using a matched filter."""

    def __init__(self, samples: Samples, radar: Radar):
        super().__init__(samples, radar)

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


class ExponentialSparseChirpProcessor(SparseChirpProcessor,
                                      ExponentialChirpProcessor):
    """Performs range processing on an exponential chirp using compressed sensing."""

    def __init__(self, samples: Samples, radar: Radar):
        super().__init__(samples, radar)

    def generate_sensing_matrix(self) -> np.ndarray:
        """Generates the sensing matrix mapping the sources to the observations.

        The dimensions of the sensing matrix should be (number of sources) x
        (number of samples).

        Returns:
            The sensing matrix.
        """
        r = self.get_output_axis()[:, np.newaxis]
        return np.exp(1j * 2 * np.pi * self.radar.beta / self.radar.alpha *
                      np.exp(self.radar.alpha * self.radar.t_axis_chirp) *
                      (1 - np.exp(-self.radar.alpha * 2 * r / self.radar.c)))


class ChirpMatchedFilterProcessorFactory:
    """Factory for a chirp processor using a matched filter."""

    # Map from chirp type to chirp processor class.
    CHIRP_PROCESSOR_MAP = {
        ChirpType.LINEAR: LinearChirpMatchedFilterProcessor,
        ChirpType.QUADRATIC: QuadraticChirpMatchedFilterProcessor,
        ChirpType.EXPONENTIAL: ExponentialChirpMatchedFilterProcessor,
    }

    @staticmethod
    def create(chirp_type: ChirpType, *args,
               **kwargs) -> ChirpMatchedFilterProcessor:
        if chirp_type not in ChirpMatchedFilterProcessorFactory.CHIRP_PROCESSOR_MAP:
            raise ValueError(f"Unimplemented chirp type: {chirp_type}.")
        return ChirpMatchedFilterProcessorFactory.CHIRP_PROCESSOR_MAP[
            chirp_type](*args, **kwargs)


class SparseChirpProcessorFactory:
    """Factory for a sparse chirp processor."""

    # Map from chirp type to chirp processor class.
    CHIRP_PROCESSOR_MAP = {
        ChirpType.LINEAR: LinearSparseChirpProcessor,
        ChirpType.QUADRATIC: QuadraticSparseChirpProcessor,
        ChirpType.EXPONENTIAL: ExponentialSparseChirpProcessor,
    }

    @staticmethod
    def create(chirp_type: ChirpType, *args, **kwargs) -> SparseChirpProcessor:
        if chirp_type not in SparseChirpProcessorFactory.CHIRP_PROCESSOR_MAP:
            raise ValueError(f"Unimplemented chirp type: {chirp_type}.")
        return SparseChirpProcessorFactory.CHIRP_PROCESSOR_MAP[chirp_type](
            *args, **kwargs)
