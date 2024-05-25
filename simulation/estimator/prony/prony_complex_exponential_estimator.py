"""The Prony complex exponential estimator estimates the parameters of complex
exponentials using Prony's method.

See https://bmcbioinformatics.biomedcentral.com/articles/10.1186/s12859-018-2473-y.
"""

from abc import ABC, abstractmethod

import numpy as np

from simulation.estimator.complex_exponential import ComplexExponentialParams
from simulation.estimator.complex_exponential_estimator import \
    ComplexExponentialEstimator
from simulation.radar.components.samples import Samples
from utils.solver.least_squares_solver import LeastSquaresMatrixVectorSolver


class PronyComplexExponentialEstimator(ComplexExponentialEstimator, ABC):
    """Complex exponential estimator using Prony's method."""

    def __init__(self, samples: Samples, fs: float) -> None:
        super().__init__(samples, fs)

    def estimate_single_exponential(self) -> ComplexExponentialParams:
        """Estimates the parameters of a single complex exponential.

        Returns:
            The estimated parameters of the complex exponential.
        """
        return self.estimate_multiple_exponentials(num_exponentials=1)[0]

    def estimate_multiple_exponentials(
            self, num_exponentials: int) -> list[ComplexExponentialParams]:
        """Estimates the parameters of multiple complex exponentials.

        Args:
            num_exponentials: Number of complex exponentials.

        Returns:
            The estimated parameters of the complex exponentials.
        """
        # Find the roots of the characteristic polynomial.
        roots = self._solve_for_roots(num_exponentials)

        # Solve for the complex exponentials' coefficients.
        complex_exponential_coefficients = self._solve_for_coefficients(roots)

        # Calculate the parameters of each complex exponential.
        params = []
        for i in range(num_exponentials):
            alpha = np.log(np.abs(roots[i])) * self.fs
            frequency = np.angle(roots[i]) * self.fs / (2 * np.pi)
            amplitude = np.abs(complex_exponential_coefficients[i])
            phase = np.angle(complex_exponential_coefficients[i])
            params.append(
                ComplexExponentialParams(frequency=frequency,
                                         phase=phase,
                                         amplitude=amplitude,
                                         alpha=alpha))
        return params

    @abstractmethod
    def _solve_for_roots(self, num_exponentials: int) -> np.ndarray:
        """Solves for the roots of the characteristic polynomial.

        Args:
            num_exponentials: Number of complex exponentials.

        Returns:
            The roots of the characteristic polynomial.
        """

    def _solve_for_coefficients(self, roots: np.ndarray) -> np.ndarray:
        """Solves for the complex exponentials' amplitudes and phases.

        Args:
            roots: Roots of the characteristic polynomial.

        Returns:
            The complex coefficients of the complex exponentials.
        """
        # To prevent numerical errors due to the geometric progression, only
        # use a few samples per root to determine the corresponding amplitude
        # and phase.
        p = len(self.samples)
        A = np.vander(roots, N=p, increasing=True).T
        b = self.samples[:p]
        solver = LeastSquaresMatrixVectorSolver(A, b)
        complex_exponential_coefficients = solver.solution
        return complex_exponential_coefficients
