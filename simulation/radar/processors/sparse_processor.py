"""The sparse processor is an interface for a processor that uses compressed
sensing, i.e., LASSO regression, to process the samples.

See https://arxiv.org/abs/1503.02339 for the paper.
"""

from abc import abstractmethod

import numpy as np
from absl import logging

from simulation.radar.components.radar import Radar
from simulation.radar.components.samples import Samples
from simulation.radar.processors.signal_processor import SignalProcessor1D
from utils.optimization.linear_model import ComplexLassoModel


class SparseProcessor1D(SignalProcessor1D):
    """Interface for a 1D sparse processor."""

    def __init__(self,
                 samples: Samples,
                 radar: Radar,
                 sparsity: int = 3,
                 epsilon: float = 0.1):
        super().__init__(samples, radar)
        self.sparsity = sparsity
        # The objective function is argmin ||x||_1 subject to ||y - Xw||_2 <=
        # epsilon, so epsilon specifies the relative noise level.
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

    @staticmethod
    def _get_kth_largest_peak_by_magnitude(array: np.ndarray, k: int) -> float:
        """Returns the kth largest peak by magnitude."""
        assert k < len(np.squeeze(array))
        sorted_array = np.sort(np.abs(array))
        return sorted_array[-k]

    def _apply_lasso(self) -> None:
        """Applies a LASSO model to find a sparse solution."""
        X = self.generate_sensing_matrix().T
        y = np.squeeze(self.samples)
        F = 0.9

        w = np.zeros(X.shape[-1])
        r = np.conjugate(X).T @ np.squeeze(self.samples).T
        M = np.empty(0)

        while len(M) < self.sparsity:
            alpha = (
                (1 - F) *
                self._get_kth_largest_peak_by_magnitude(r, self.sparsity) + F *
                self._get_kth_largest_peak_by_magnitude(r, self.sparsity + 1))
            lasso_model = ComplexLassoModel(X, y, alpha)
            lasso_model.solve()
            w = lasso_model.get_coefficients()
            r = np.conjugate(X).T @ (y - X @ w)
            M = np.squeeze(
                np.argwhere(
                    np.abs(w) > self.epsilon * np.linalg.norm(w, np.inf)))
        if len(M) > self.sparsity:
            M = np.squeeze(
                np.argwhere(
                    np.abs(w) > self._get_kth_largest_peak_by_magnitude(
                        np.abs(w), self.sparsity)))

        w = np.zeros(X.shape[-1])
        w[M] = np.linalg.pinv(X[:, M]) @ y
        self.samples = w * X.shape[-1]
        logging.debug("Alpha: %f, |M|: %d.", alpha, len(M))
