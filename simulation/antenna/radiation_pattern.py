"""The radiation pattern represents the radiation pattern of an antenna or
antenna array.
"""

import numpy as np

from utils import constants


class RadiationPattern:
    """Radiation pattern.

    The radiation pattern is assumed in the far field of the antenna and is
    measured in units of power.

    Attributes:
        azimuth: Azimuth in radians.
        elevation: Elevation in radians.
        radiation_pattern: Radiation pattern.
    """

    def __init__(
        self,
        radiation_pattern: np.ndarray,
        azimuth: np.ndarray,
        elevation: np.ndarray,
    ) -> None:
        shape = np.shape(radiation_pattern)
        self.radiation_pattern = radiation_pattern
        self.azimuth = np.broadcast_to(azimuth, shape)
        self.elevation = np.broadcast_to(elevation, shape)

    def db(self, log_plus_one: bool = True) -> np.ndarray:
        """Returns the radiation pattern in dB.

        Args:
            log_plus_one: If true, add 1 prior to taking the logarithm to
              handle any zero values.
        """
        if log_plus_one:
            return constants.power2db(self.radiation_pattern + 1)
        return constants.power2db(self.radiation_pattern)

    def normalized_db(self, log_plus_one: bool = True) -> np.ndarray:
        """Returns the normalized radiation pattern in dB.

        Args:
            log_plus_one: If true, add 1 prior to taking the logarithm to
              handle any zero values.
        """
        return self.db(log_plus_one) - self.max_db(log_plus_one)

    def max(self) -> np.ndarray:
        """Returns the maximum power magnitude in the radiation pattern."""
        return np.max(self.radiation_pattern)

    def max_db(self, log_plus_one: bool = True) -> np.ndarray:
        """Returns the maximum power magnitude in dB in the radiation pattern.

        Args:
            log_plus_one: If true, add 1 prior to taking the logarithm to
              handle any zero values.
        """
        if log_plus_one:
            return constants.power2db(self.max() + 1)
        return constants.power2db(self.max())

    def min(self) -> np.ndarray:
        """Returns the minimum power magnitude in the radiation pattern."""
        return np.min(self.radiation_pattern)

    def min_db(self, log_plus_one: bool = True) -> np.ndarray:
        """Returns the minimum power magnitude in dB in the radiation pattern.

        Args:
            log_plus_one: If true, add 1 prior to taking the logarithm to
              handle any zero values.
        """
        if log_plus_one:
            return constants.power2db(self.min() + 1)
        return constants.power2db(self.min() + 1)

    def main_lobe_width(
        self,
        peak_index: int | list[int] | np.ndarray,
        axis: int = -1,
    ) -> float | np.ndarray:
        """Finds the main lobe width along the given axes according to the
        corresponding azimuth or elevation axis.

        This function assumes that the radiation pattern wraps around.

        Args:
            peak_index: Peak index.
            axis: Axes along which to find the main lobe width. If -1, find the
              main lobe width along all axes.

        Returns:
            The main lobe width along the given axes.
        """
        if np.isscalar(peak_index):
            peak_index = [peak_index]

        num_dimensions = self.radiation_pattern.ndim
        axis_indices = np.arange(num_dimensions) if axis < 0 else [axis]
        axes = (self.azimuth, self.elevation)

        main_lobe_widths = np.zeros(len(axis_indices))
        for axis_index, axis in enumerate(axis_indices):
            slice_index = (*peak_index[:axis_index], slice(None),
                           *peak_index[axis_index + 1:])
            main_lobe_width = self._main_lobe_width(
                self.radiation_pattern[slice_index],
                peak_index[axis_index],
                axes[axis][slice_index],
            )
            main_lobe_widths[axis_index] = main_lobe_width
        return np.squeeze(main_lobe_widths)

    def _main_lobe_width(
        self,
        data: np.ndarray,
        peak_index: int,
        axis: np.ndarray,
    ) -> float:
        """Finds the main lobe width along the one-dimensional data array.

        Args:
            data: Data along which to find the main lobe width.
            peak_index: Peak index.
            axis: Axis values.

        Returns:
            The main lobe width along the given axis.
        """
        peak_value = data[peak_index]

        # The main lobe width is defined as the full width at half maximum.
        threshold = peak_value / 2
        below_threshold = data < threshold

        # Find the range of the axis.
        # The axis values are assumed to be equally spaced.
        axis_range = len(axis) * np.diff(axis)[0]

        # Extend the data because to handle wraparounds.
        peak_index_extended = peak_index + len(data)
        below_threshold_extended = np.tile(below_threshold, 3)
        below_threshold_extended_diff = np.diff(below_threshold_extended)
        threshold_indices = np.where(below_threshold_extended_diff)[0]

        # Find the points at half maximum of the main lobe.
        for i in range(1, len(threshold_indices)):
            if (threshold_indices[i - 1] <= peak_index_extended and
                    threshold_indices[i] >= peak_index_extended):
                difference = (axis[threshold_indices[i] % len(data)] -
                              axis[threshold_indices[i - 1] % len(data)])
                return difference % axis_range
        return axis_range
