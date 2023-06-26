"""The peak selector class contains various utilities for selecting peaks from
a collection of samples by magnitude.
"""

import numpy as np

from simulation.radar.components.samples import Samples


class PeakSelector(Samples):
    """Selects peaks by magnitude."""

    def __init__(self,
                 samples: Samples,
                 guard_length: int = 0,
                 wrap: bool = True):
        super().__init__(samples)
        self.guard_length = guard_length
        self.wrap = wrap

    def get_largest_peak_index(self) -> np.ndarray:
        """Returns the index of the largest peak."""
        return self.get_kth_largest_peak_index(0)

    def get_largest_peak_magnitude(self) -> float:
        """Returns the magnitude of the largest peak."""
        return self.get_kth_largest_peak_magnitude(0)

    def get_kth_largest_peak_index(self, k: int) -> np.ndarray:
        """Returns the index of the kth largest peak.

        Args:
            k: Index of the largest peak.
        """
        k_largest_peaks_indices = self._get_k_largest_peaks_index(k + 1)
        return k_largest_peaks_indices[:, k]

    def get_kth_largest_peak_magnitude(self, k: int) -> float:
        """Returns the magnitude of the kth largest peak.

        Args:
            k: Index of the largest peak.
        """
        k_largest_peaks_magnitudes = self.get_k_largest_peaks_magnitude(k + 1)
        return k_largest_peaks_magnitudes[k]

    def get_k_largest_peaks_index(self, k: int) -> tuple[np.ndarray, ...]:
        """Gets the indices of the k largest peaks.

        Args:
            k: Index of the largest peak.
            guard_length: Number of indices between peaks.

        Returns:
            A tuple of the indices of the k largest peaks in order of decreasing
            magnitude. The tuple consists of (number of dimensions in the
            samples) arrays, each of length k.
        """
        peak_indices = self._get_k_largest_peaks_index(k)
        return tuple(peak_indices[k] for k in range(len(peak_indices)))

    def get_k_largest_peaks_magnitude(self, k: int) -> np.ndarray:
        """Gets the magnitudes of the k largest peaks.

        Args:
            k: Index of the largest peak.
            guard_length: Number of indices between peaks.

        Returns:
            The magnitudes of the k largest peaks in order of decreasing
            magnitude.
        """
        return self.get_abs_samples()[self.get_k_largest_peaks_index(k)]

    def _get_k_largest_peaks_index(self, k: int) -> np.ndarray:
        """Gets the indices of the k largest peaks.

        Args:
            k: Index of the largest peak.
            guard_length: Number of indices between peaks.

        Returns:
            The indices of the k largest peaks in order of decreasing magnitude.
            The dimensions are (number of dimensions in the samples) x k.
        """
        # Copy the samples because we will mutate them.
        samples_abs = Samples(self.get_abs_samples())
        peak_indices = np.zeros((samples_abs.ndim, k), dtype=np.int64)
        for i in range(k):
            peak_index = np.unravel_index(np.argmax(samples_abs.samples),
                                          samples_abs.shape)
            peak_indices[..., i] = peak_index
            # Set the peak to the minimum magnitude.
            samples_abs.samples[peak_index] = -np.inf
            # Set bins within the guard length to the minimum magnitude.
            neighbor_indices = self._get_neighbor_indices(peak_index)
            samples_abs.samples[neighbor_indices] = -np.inf
        return peak_indices

    def _get_neighbor_indices(self,
                              index: tuple[int, ...]) -> tuple[np.ndarray, ...]:
        """Gets the indices of the neighboring bins.

        Args:
            index: Index of the center bin.

        Returns:
            A tuple of the indices of the neighbors. The tuple consists of
            (number of dimensions in the samples) arrays.
        """
        diffs = [
            np.arange(-self.guard_length, self.guard_length + 1)
            for _ in range(self.ndim)
        ]
        neighbor_indices = np.meshgrid(*diffs)
        num_dims = len(neighbor_indices)
        neighbor_indices = [
            neighbor_indices[i].flatten() + index[i] for i in range(num_dims)
        ]
        if self.wrap:
            # Negative indices and indices that are greater than the
            # corresponding axis lengths wrap around.
            for i in range(num_dims):
                neighbor_indices[i] = neighbor_indices[i] % self.shape[i]
        else:
            # Discard negative indices and indices that are greater than the
            # corresponding axis lengths.
            invalid_row_masks = [
                condition(neighbor_indices[i], i)
                for i in range(num_dims)
                for condition in (lambda index, i: index < 0,
                                  lambda index, i: index >= self.shape[i])
            ]
            invalid_row_mask = np.logical_or.reduce(invalid_row_masks)
            neighbor_indices = [
                neighbor_indices[i][np.invert(invalid_row_mask)]
                for i in range(num_dims)
            ]
        return tuple(neighbor_indices)
