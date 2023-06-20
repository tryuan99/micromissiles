"""The matched filter processor is an interface for a 2D matched filter processor."""

from abc import abstractmethod

import numpy as np

from simulation.radar.components.radar import Radar
from simulation.radar.components.samples import Samples
from simulation.radar.processors.signal_processor import (SignalProcessor1D,
                                                          SignalProcessor2D)


class MatchedFilterProcessor1D(SignalProcessor1D):
    """Interface for a 1D matched filter processor."""

    def __init__(self, samples: Samples, radar: Radar):
        super().__init__(samples, radar)

    def process_samples(self) -> None:
        """Processes the 1D samples."""
        self._apply_matched_filter()

    @abstractmethod
    def generate_matched_filter(self, value: float) -> np.ndarray:
        """Generates the 1D matched filter against which the samples will be correlated.

        The size of the matched filter should be compatible with the samples.

        Args:
            value: Value for the dimension to be processed.

        Returns:
            A 1D matched filter for the given axis value.
        """

    def _apply_matched_filter(self) -> None:
        """Applies a 1D matched filter."""
        matched_filter_out = np.zeros(
            (*self.samples.shape[:-1], *self.get_output_shape()),
            dtype=np.complex128)
        matched_filter = self.generate_matched_filter(
            self.get_output_axis()[..., np.newaxis])
        self.samples = np.conjugate(matched_filter) @ np.squeeze(self.samples)


class MatchedFilterProcessor2D(SignalProcessor2D):
    """Interface for a 2D matched filter processor."""

    def __init__(self, samples: Samples, radar: Radar):
        super().__init__(samples, radar)

    def process_samples(self) -> None:
        """Processes the 2D samples."""
        self._apply_matched_filter()

    @abstractmethod
    def generate_matched_filter(self, axis1_value: float,
                                axis2_value: float) -> np.ndarray:
        """Generates the 2D matched filter against which the samples will be correlated.

        The size of the matched filter should be compatible with the last two dimensions
        of the samples.

        Args:
            axis1_value: Value for the first dimension.
            axis2_value: Value for the second dimension.

        Returns:
            A 2D matched filter for the given first and second dimension values.
        """

    def _apply_matched_filter(self) -> None:
        """Applies a 2D matched filter."""
        matched_filter_out = np.zeros(
            (*self.samples.shape[:-2], *self.get_output_shape()),
            dtype=np.complex128)
        for axis1_index, axis1_value in enumerate(self.get_output_axis1()):
            for axis2_index, axis2_value in enumerate(self.get_output_axis2()):
                matched_filter = self.generate_matched_filter(
                    axis1_value, axis2_value)
                matched_filter_out[..., axis1_index, axis2_index] = np.sum(
                    np.multiply(self.samples, np.conjugate(matched_filter)),
                    axis=(-2, -1))
        self.samples = matched_filter_out
