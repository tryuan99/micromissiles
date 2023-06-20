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
        """Returns the title of the spectrum."""
        return "Range processing"

    @property
    def label_axis(self) -> str:
        """Returns the label of the range axis."""
        return "Range in m"

    def get_window(self) -> np.ndarray:
        """Returns the range window."""
        return self.radar.window_r

    def get_output_axis(self) -> np.ndarray:
        """Returns the range axis."""
        return self.radar.r_axis


class ChirpFftProcessor(FftProcessor1D, ChirpProcessor):
    """Performs range processing using a 1D FFT."""

    def __init__(self, samples: Samples, radar: Radar):
        super().__init__(samples, radar)


class LinearChirpProcessor(MatchedFilterProcessor1D, ChirpProcessor):
    """Performs range processing on a linear chirp using a matched filter."""

    def __init__(self, samples: Samples, radar: Radar):
        super().__init__(samples, radar)


class QuadraticChirpProcessor(MatchedFilterProcessor1D, ChirpProcessor):
    """Performs range processing on a quadratic chirp using a matched filter."""

    def __init__(self, samples: Samples, radar: Radar):
        super().__init__(samples, radar)


class ExponentialChirpProcessor(MatchedFilterProcessor1D, ChirpProcessor):
    """Performs range processing on an exponential chirp using a matched filter."""

    def __init__(self, samples: Samples, radar: Radar):
        super().__init__(samples, radar)


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
        if chirp_type not in CHIRP_PROCESSOR_MAP:
            raise ValueError(f"Unimplemented chirp type: {chirp_type}.")
        return CHIRP_PROCESSOR_MAP[chirp_type](*args, **kwargs)
