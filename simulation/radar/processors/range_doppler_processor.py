"""The range-Doppler processor performs the range and Doppler processing on the ADC samples."""

import numpy as np

from simulation.radar.components.radar import Radar
from simulation.radar.components.samples import Samples
from simulation.radar.processors.fft_processor import FftProcessor2D
from simulation.radar.processors.matched_filter_processor import \
    MatchedFilterProcessor2D
from simulation.radar.processors.signal_processor import SignalProcessor2D


class RangeDopplerProcessor(SignalProcessor2D):
    """Interface for a range-Doppler processor.

    The first dimension is Doppler, and the second dimension is range.
    """

    def __init__(self, samples: Samples, radar: Radar):
        super().__init__(samples, radar)

    @property
    def title(self) -> str:
        """Returns the title of the 2D spectrum."""
        return "Range-Doppler map"

    @property
    def label_axis1(self) -> str:
        """Returns the label of the Doppler axis."""
        return "Range rate in m/s"

    @property
    def label_axis2(self) -> str:
        """Returns the label of the range axis."""
        return "Range in m"

    def get_window_axis1(self) -> np.ndarray:
        """Returns the Doppler window."""
        return self.radar.window_v

    def get_window_axis2(self) -> np.ndarray:
        """Returns the range window."""
        return self.radar.window_r

    def get_output_axis1(self) -> np.ndarray:
        """Returns the range axis."""
        return self.radar.v_axis

    def get_output_axis2(self) -> np.ndarray:
        """Returns the Doppler axis."""
        return self.radar.r_axis

    def accumulate_log_magnitude(self) -> Samples:
        """Returns the log magnitude of the samples accumulated over all RX antennas.

        The accumulated range-Doppler map is intended for CFAR.
        The third-to-last dimension is for the RX antennas.
        """
        # mmWave SDK uses a logarithmic CFAR with a base-2 logarithm.
        return Samples(
            np.squeeze(
                np.apply_over_axes(np.sum, np.log2(np.abs(self.samples)),
                                   (0, -3))))


class RangeDopplerFftProcessor(FftProcessor2D, RangeDopplerProcessor):
    """Performs range and Doppler processing using a 2D FFT."""

    def __init__(self, samples: Samples, radar: Radar):
        super().__init__(samples, radar)

    def process_samples(self) -> None:
        """Processes the 2D samples."""
        self.apply_2d_fft()
        # Perform an FFT shift in the Doppler dimension.
        self.fft_shift_axis1()


class RangeDopplerMatchedFilterProcessor(MatchedFilterProcessor2D,
                                         RangeDopplerProcessor):
    """Performs range and Doppler processor using a 2D matched filter.

    The 2D matched filter compensates for range cell migration and for the
    Doppler shift.
    The 2D matched filter is especially useful when v or mu is large.
    """

    def __init__(self, samples: Samples, radar: Radar):
        super().__init__(samples, radar)

    def generate_matched_filter(self, axis1_value: float,
                                axis2_value: float) -> np.ndarray:
        """Generates the 2D matched filter against which the ADC samples will be correlated.

        Args:
            axis1_value: Doppler value.
            axis2_value: Range value.

        Returns:
            A 2D matched filter for the given range and Doppler values.
        """
        r, v = axis2_value, axis1_value
        return np.exp(1j * 2 * np.pi * 2 / self.radar.c * np.multiply(
            r + v * self.radar.t_axis,
            self.radar.mu *
            np.repeat([self.radar.t_axis_chirp], self.radar.N_v, axis=0) +
            self.radar.f0))
