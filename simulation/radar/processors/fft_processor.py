"""The FFT processor is an interface for a 2D FFT processor, e.g., a range-Doppler map.

The FFT processor applies a 2D FFT to process the samples.
"""

from abc import ABC, abstractmethod

import numpy as np

from simulation.radar.components.radar import Radar
from simulation.radar.components.samples import Samples
from simulation.radar.processors.signal_processor import SignalProcessor


class FftProcessor(SignalProcessor, ABC):
    """Interface for a 2D FFT processor."""

    def __init__(self, samples: Samples, radar: Radar):
        super().__init__(samples, radar)

    def process_2d_samples(self) -> None:
        """Processes the 2D samples."""
        self.apply_2d_fft()

    def apply_fft_axis1(self) -> None:
        """Applies an FFT along the first dimension."""
        self.samples = np.fft.fft(self.samples,
                                  self.get_output_shape()[0],
                                  axis=-2)

    def apply_fft_axis2(self) -> None:
        """Applies an FFT along the second dimension."""
        self.samples = np.fft.fft(self.samples,
                                  self.get_output_shape()[1],
                                  axis=-1)

    def apply_2d_fft(self) -> None:
        """Applies a 2D FFT."""
        self.samples = np.fft.fft2(self.samples, self.get_output_shape())

    def fft_shift_axis1(self) -> None:
        """Performs an FFT shift in the first dimension."""
        self.samples = np.fft.fftshift(self.samples, axes=-2)

    def fft_shift_axis2(self) -> None:
        """Performs an FFT shift in the second dimension."""
        self.samples = np.fft.fftshift(self.samples, axes=-1)

    def fft_shift_2d(self) -> None:
        """Performs an FFT shift in both processed dimensions."""
        self.samples = np.fft.fftshift(self.samples, axes=(-2, -1))
