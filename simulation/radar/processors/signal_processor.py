"""The signal processor is an interface for a 2D signal processor, e.g., a
range-Doppler map.

The two dimensions that will be processed are the last two dimensions of the
samples matrix.
"""

from abc import ABC, abstractmethod

import numpy as np

from simulation.radar.components.radar import Radar
from simulation.radar.components.samples import Samples


class SignalProcessor(Samples, ABC):
    """Interface for a 2D signal processor."""

    def __init__(self, samples: Samples, radar: Radar):
        super().__init__(samples)
        self.radar = radar

    @abstractmethod
    def get_window_axis1(self) -> np.ndarray:
        """Returns the window for the samples along the first dimension."""

    @abstractmethod
    def get_window_axis2(self) -> np.ndarray:
        """Returns the window for the samples along the second dimension."""

    def apply_window_axis1(self) -> None:
        """Applies a window to the first dimension to be processed."""
        self.samples = self.samples * self.get_window_axis1()[..., np.newaxis]

    def apply_window_axis2(self) -> None:
        """Applies a window to the second dimension to be processed."""
        self.samples = (self.samples *
                        self.get_window_axis2()[..., np.newaxis, :])

    def apply_2d_window(self) -> None:
        """Applies a 2D window.

        This function should be called before processing the 2D samples.
        """
        self.apply_window_axis1()
        self.apply_window_axis2()

    @abstractmethod
    def get_output_axis1(self) -> np.ndarray:
        """Returns the axis for the first dimension of the 2D output."""

    @abstractmethod
    def get_output_axis2(self) -> np.ndarray:
        """Returns the axis for the second dimension of the 2D output."""

    def get_output_shape(self) -> tuple[int, int]:
        """Returns the 2D output shape after processing.

        The 2D output shape is a length-2 integer tuple representing the number
        of output bins in the two processed dimensions.
        """
        return (len(self.get_output_axis1()), len(self.get_output_axis2()))

    @abstractmethod
    def process_2d_samples(self) -> None:
        """Processes the 2D samples."""
