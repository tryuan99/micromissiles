"""The sparse processor is an interface for a processor that uses compressed
sensing, i.e., LASSO regression, to process the samples.

See https://arxiv.org/abs/1503.02339 for the paper.
"""

from abc import abstractmethod

import numpy as np
from absl import logging

from simulation.radar.components.peak_selector import PeakSelector
from simulation.radar.components.radar import Radar
from simulation.radar.components.samples import Samples
from simulation.radar.processors.signal_processor import SignalProcessor1D
from utils.optimization.linear_model import ComplexLassoModel


class SparseProcessor1D(SignalProcessor1D):
    """Interface for a 1D sparse processor."""

    def __init__(self, samples: Samples, radar: Radar, sparsity: int,
                 guard_length: int, epsilon: float):
        super().__init__(samples, radar)
        self.sparsity = sparsity
        # The guard length is the minimum number of bins in each dimension
        # between peaks.
        self.guard_length = guard_length
        # Epsilon specifies when the iterative LASSO algorithm should halt.
        self.epsilon = epsilon

    def process_samples(self) -> None:
        """Processes the 1D samples."""
        self._apply_lasso()

    @abstractmethod
    def generate_sensing_matrix(self) -> np.ndarray:
        """Generates the sensing matrix mapping the sources to the observations.

        The dimensions of the sensing matrix should be (number of sources) x
        (number of samples).

        Returns:
            The sensing matrix.
        """

    def _get_kth_largest_peak_magnitude(self, array: np.ndarray,
                                        k: int) -> float:
        """Returns the magnitude of the kth largest peak."""
        peak_selector = PeakSelector(array, self.guard_length, False)
        return peak_selector.get_kth_largest_peak_magnitude(k)

    def _apply_pocs(self) -> None:
        """Applies a projection over convex sets (POCS) algorithm.

        The signal is sparse int he frequency domain, and we use the Fourier
        transform as an incoherent basis. We undersample in the time domain and
        estimate the signal with LASSO.

        See https://people.eecs.berkeley.edu/~mlustig/CS/CS_ex.pdf for more
        details.
        """
        X = self.generate_sensing_matrix().T
        y = np.squeeze(self.samples)

    def _apply_lasso(self) -> None:
        """Applies a LASSO model to find a sparse solution."""
        X = self.generate_sensing_matrix().T
        y = np.squeeze(self.samples)
        F = 0.9

        w = np.zeros(X.shape[-1])
        r = np.conjugate(X).T @ np.squeeze(self.samples).T
        M = np.empty(0)

        while len(M) < self.sparsity:
            lmbda = (
                (1 - F) *
                self._get_kth_largest_peak_magnitude(r, self.sparsity) +
                F * self._get_kth_largest_peak_magnitude(r, self.sparsity + 1))
            lasso_model = ComplexLassoModel(X, y, lmbda)
            lasso_model.solve()
            w = lasso_model.get_coefficients()
            r = np.conjugate(X).T @ (y - X @ w)
            M = np.squeeze(
                np.argwhere(
                    np.abs(w) > self.epsilon * np.linalg.norm(w, np.inf)))
        if len(M) > self.sparsity:
            # TODO(titan): Figure out a better way to compensate for the path loss.
            scaling_factor = np.sqrt(self.radar.r_axis**4)
            peak_selector = PeakSelector(w, self.guard_length, False,
                                         scaling_factor)
            M = peak_selector.get_k_largest_peaks_index(self.sparsity)[0]

        w = np.zeros(X.shape[-1], dtype=np.complex128)
        w[M] = np.linalg.pinv(X[:, M]) @ y
        self.samples = w * X.shape[-1]
        logging.debug("Lambda: %f, |M|: %d.", lmbda, len(M))
