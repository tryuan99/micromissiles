"""The signal processor is an interface for a signal processor, e.g., a range-
Doppler map.

The dimensions that will be processed are the last dimensions of the samples
matrix, i.e., for a 2D signal processor, the last two dimensions of the
samples matrix will be processed.
"""

from abc import ABC, abstractmethod

import matplotlib.pyplot as plt
import numpy as np

from simulation.radar.components.radar import Radar
from simulation.radar.components.samples import Samples
from utils import constants
from utils.visualization.color_maps import COLOR_MAPS


class SignalProcessor(Samples, ABC):
    """Interface for a signal processor."""

    def __init__(self, samples: Samples, radar: Radar):
        super().__init__(samples)
        self.radar = radar

    @property
    @abstractmethod
    def title(self) -> str:
        """Returns the title of the spectrum."""

    @abstractmethod
    def get_output_shape(self) -> tuple[int, ...]:
        """Returns the output shape after processing."""

    @abstractmethod
    def process_samples(self) -> None:
        """Processes the samples."""

    @abstractmethod
    def estimate_peak(self) -> tuple[float, ...]:
        """Estimates the bin(s) corresponding the peak.

        This function should only be used if there is a unique peak in the
        spectrum.

        Returns:
            A tuple consisting of the estimated axis values at the peak.
        """

    @abstractmethod
    def plot_spectrum(self) -> None:
        """Plots the processeds spectrum."""


class SignalProcessor1D(SignalProcessor):
    """Interface for a 1D signal processor."""

    def __init__(self, samples: Samples, radar: Radar):
        super().__init__(samples, radar)

    @property
    @abstractmethod
    def label_axis(self) -> str:
        """Returns the label of the dimension to be processed."""

    @abstractmethod
    def get_window(self) -> np.ndarray:
        """Returns the window for the samples."""

    def apply_window(self) -> None:
        """Applies a window to the samples to be processed."""
        self.samples = self.samples * self.get_window()

    @abstractmethod
    def get_output_axis(self) -> np.ndarray:
        """Returns the axis for the output."""

    def get_output_shape(self) -> tuple[int]:
        """Returns the 1D output shape after processing."""
        return len(self.get_output_axis()),

    def estimate_peak(self) -> tuple[float]:
        """Estimates the bin corresponding the peak.

        This function should only be used if there is a unique peak in the 1D
        spectrum.

        Returns:
            A tuple consisting of the estimated bin value at the peak.
        """
        index = np.argmax(np.squeeze(self.get_abs_samples()))
        return self.get_output_axis()[index]

    def plot_spectrum(self) -> None:
        """Plots the processed 1D spectrum."""
        fig, ax = plt.subplots(figsize=(12, 8))
        plt.plot(self.get_output_axis(),
                 constants.mag2db(np.squeeze(self.get_abs_samples())))
        ax.set_title(self.title)
        ax.set_xlabel(self.label_axis)
        ax.set_ylabel("Magnitude in dB")
        plt.show()


class SignalProcessor2D(SignalProcessor):
    """Interface for a 2D signal processor."""

    def __init__(self, samples: Samples, radar: Radar):
        super().__init__(samples, radar)

    @property
    @abstractmethod
    def label_axis1(self) -> str:
        """Returns the label of the first dimension."""

    @property
    @abstractmethod
    def label_axis2(self) -> str:
        """Returns the label of the second dimension."""

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

    def estimate_peak(self) -> tuple[float, float]:
        """Estimates the 2D bins corresponding the peak.

        This function should only be used if there is a unique peak in the 2D
        spectrum.

        Returns:
            A tuple consisting of the estimated (axis 1, axis 2) values of the
            peak.
        """
        axis1_index, axis2_index = np.unravel_index(
            np.argmax(np.squeeze(self.get_abs_samples())), self.shape[-2:])
        return (self.get_output_axis1()[axis1_index],
                self.get_output_axis2()[axis2_index])

    def plot_spectrum(self) -> None:
        """Plots the processed 2D spectrum."""
        fig, ax = plt.subplots(
            figsize=(12, 8),
            subplot_kw={"projection": "3d"},
        )
        surf = ax.plot_surface(
            *np.meshgrid(self.get_output_axis1(), self.get_output_axis2()),
            constants.mag2db(np.squeeze(self.get_abs_samples())).T,
            cmap=COLOR_MAPS["parula"],
            antialiased=False,
        )
        ax.set_title(self.title)
        ax.set_xlabel(self.label_axis1)
        ax.set_ylabel(self.label_axis2)
        ax.view_init(45, -45)
        plt.colorbar(surf)
        plt.show()
