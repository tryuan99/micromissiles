"""The radiation pattern represents the radiation pattern of an antenna or
antenna array.
"""

import itertools

import numpy as np

from utils import constants

# If there are no sidelobes, the sidelobe level is infinite. However, returning
# infinity causes problems with the multi-objective optimizer, so return a
# large sidelobe level instead.
SIDELOBE_LEVEL_INFINITE = 100  # dB


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

    def main_lobe_boundaries(
        self,
        peak_index: int | list[int] | np.ndarray,
        axis: int = None,
    ) -> np.ndarray:
        """Finds the indices of the main lobe boundaries along the given axes.

        This function assumes that the radiation pattern wraps around.

        Args:
            peak_index: Peak index.
            axis: Axes along which to find the main lobe. If None, find the
              main lobe along all axes.

        Returns:
            The indices of the main lobe boundaries along the given axes.
        """
        peak_index = (np.array([peak_index])
                      if np.isscalar(peak_index) else np.array(peak_index))
        axis_indices = (np.arange(self.radiation_pattern.ndim)
                        if axis is None else np.array([axis]))

        # Find the main lobe boundaries for each axis.
        main_lobe_boundaries = np.zeros((len(axis_indices), 2), dtype=np.int64)
        for axis_index, axis in enumerate(axis_indices):
            main_lobe_axis_boundaries = self._main_lobe_boundaries(
                self._slice_data(self.radiation_pattern, peak_index,
                                 axis_index),
                peak_index[axis_index],
            )
            main_lobe_boundaries[axis_index] = main_lobe_axis_boundaries
        return main_lobe_boundaries

    @staticmethod
    def _main_lobe_boundaries(
        data: np.ndarray,
        peak_index: int,
    ) -> np.ndarray:
        """Finds the indices of the main lobe boundaries along the one-
        dimensional data array.

        Args:
            data: Data along which to find the main lobe.
            peak_index: Peak index.

        Returns:
            The indices of the main lobe boundaries.
        """
        peak_value = data[peak_index]

        # The main lobe width is defined as the full width at half maximum.
        threshold = peak_value / 2
        below_threshold = data <= threshold

        # Extend the data because to handle wraparounds.
        peak_index_extended = peak_index + len(data)
        below_threshold_extended = np.tile(below_threshold, 3)
        below_threshold_extended_diff = np.diff(below_threshold_extended)
        threshold_indices = np.where(below_threshold_extended_diff)[0]

        # Find the points at half maximum of the main lobe.
        for i in range(1, len(threshold_indices)):
            if ((threshold_indices[i - 1] <= peak_index_extended) and
                (threshold_indices[i] >= peak_index_extended)):
                return np.array([
                    threshold_indices[i - 1] % len(data),
                    threshold_indices[i] % len(data),
                ])

        # If the half maximum was not found, signify that the main lobe
        # occupies the entire axis.
        return np.zeros(2)

    def main_lobe_width(
        self,
        peak_index: int | list[int] | np.ndarray,
        axis: int = None,
    ) -> float | np.ndarray:
        """Finds the main lobe width along the given axes in the units of the
        axis.

        This function assumes that the radiation pattern wraps around.

        Args:
            peak_index: Peak index.
            axis: Axes along which to find the main lobe width. If None, find
              the main lobe width along all axes.

        Returns:
            The main lobe width along the given axes in the units of the axis.
        """
        peak_index = (np.array([peak_index])
                      if np.isscalar(peak_index) else np.array(peak_index))
        main_lobe_boundaries = self.main_lobe_boundaries(peak_index, axis)
        axes = (self.azimuth, self.elevation)

        # Find the main lobe width for each axis.
        main_lobe_widths = np.zeros(len(main_lobe_boundaries))
        for axis_index in range(len(main_lobe_boundaries)):
            # Slice along the corresponding axis.
            axis = self._slice_data(axes[axis_index], peak_index, axis_index)

            # Find the range of the axis. The axis values are assumed to be
            # equally spaced.
            axis_range = len(axis) * np.diff(axis)[0]

            # Find the main lobe width in the units of the axis.
            axis_values = axis[main_lobe_boundaries[axis_index]]
            difference = np.diff(axis_values)[0]

            # If the main lobe has a width of 0, the main lobe actually spans
            # the entire axis.
            if difference != 0:
                main_lobe_widths[axis_index] = difference % axis_range
            else:
                main_lobe_widths[axis_index] = axis_range
        return np.squeeze(main_lobe_widths)

    def sidelobe_level(
        self,
        peak_index: int | list[int] | np.ndarray,
        axis: int = None,
    ) -> float:
        """Calculates the sidelobe level in dB along the given axes.

        This function assumes that the radiation pattern wraps around.

        Args:
            peak_index: Peak index.
            axis: Axes along which to find the sidelobe level. If None,
              consider all axes.

        Returns:
            The sidelobe level in dB relative to the main lobe.
        """
        peak_index = (np.array([peak_index])
                      if np.isscalar(peak_index) else np.array(peak_index))
        data = self._slice_data(self.radiation_pattern, peak_index, axis)
        peak_value = data[tuple(peak_index)]

        # Find the local maxima and the corresponding values.
        local_maximum_indices = self._find_local_maxima(data)
        local_maximum_values = self.radiation_pattern[local_maximum_indices]
        local_maximum_indices = np.array(local_maximum_indices).T

        # Find the main lobe boundaries.
        # The main lobe boundary indices may wrap around.
        main_lobe_boundaries = self.main_lobe_boundaries(peak_index, axis)
        main_lobe_lower_boundaries = main_lobe_boundaries[:, 0]
        main_lobe_upper_boundaries = main_lobe_boundaries[:, 1]
        wrapped_around_boundaries = (main_lobe_lower_boundaries
                                     > main_lobe_upper_boundaries)

        # Sort the local maximum values in descending order.
        sorted_maximum_values_indices = np.argsort(local_maximum_values)[::-1]

        # Return the highest sidelobe level that is not in the main lobe.
        for maximum_value_index in sorted_maximum_values_indices:
            # Check whether the local maximum lies outside of the main lobe.
            local_maximum_index = local_maximum_indices[maximum_value_index]
            less_than_lower_boundaries = (local_maximum_index
                                          <= main_lobe_lower_boundaries)
            greater_than_upper_boundaries = (local_maximum_index
                                             > main_lobe_upper_boundaries)
            # If the main lobe boundary does not wrap around, check that the
            # local maximum is less than the lower boundary or greater than the
            # upper boundary. If the main lobe boundary wraps around, check
            # that the local maximum is less than the lower boundary and
            # greater than the upper boundary.
            if np.all(
                ((less_than_lower_boundaries | greater_than_upper_boundaries) &
                 ~wrapped_around_boundaries) |
                ((less_than_lower_boundaries & greater_than_upper_boundaries) &
                 wrapped_around_boundaries)):
                sidelobe_value = local_maximum_values[maximum_value_index]
                return constants.power2db(peak_value / sidelobe_value)

        # If there are no sidelobes, the sidelobe level is infinite.
        return SIDELOBE_LEVEL_INFINITE

    @staticmethod
    def _find_local_maxima(data: np.ndarray) -> tuple[np.ndarray]:
        """Finds the local maxima in the radiation pattern.

        The radiation pattern is assumed to be no more than 2-dimensional.

        Args:
            data: Data for which to find the local maxima.

        Returns:
            An array containing the indices corresponding to the local maxima.
        """
        local_maxima = np.full(data.shape, True)

        # Shift the data to check each element against its neighbors, including
        # diagonal neighbors.
        shifts = itertools.product([-1, 0, 1], repeat=data.ndim)
        for shift in shifts:
            shifted_data = np.roll(data, shift, axis=np.arange(data.ndim))
            larger_than_shifted = data >= shifted_data
            # A local maximum must be larger than any of its neighbors,
            # including diagonal neighbors.
            local_maxima &= larger_than_shifted

        # Return the indices of the local maxima.
        return np.nonzero(local_maxima)

    @staticmethod
    def _slice_data(data: np.ndarray,
                    index: int | list[int] | np.ndarray,
                    axis: int = None) -> np.ndarray:
        """Slices the data along the given axis at the given index.

        Args:
            data: Data to slice.
            index: Index into the data.
            axis: Axis to slice.

        Returns:
            The slice along the given axis at the given index.
        """
        if axis is None:
            return data
        # Preserve the index for the axes along which is not being sliced.
        slice_index = (
            *index[:axis],
            slice(None),
            *index[axis + 1:],
        )
        return data[slice_index]
