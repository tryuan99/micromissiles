"""The Prony polynomial complex exponential estimator estimates the parameters
of complex exponentials using the polynomial method.

See https://bmcbioinformatics.biomedcentral.com/articles/10.1186/s12859-018-2473-y.
"""

import numpy as np
import scipy.linalg

from simulation.estimator.prony.prony_complex_exponential_estimator import \
    PronyComplexExponentialEstimator
from simulation.radar.components.samples import Samples
from utils.solver.least_squares_solver import LeastSquaresMatrixVectorSolver
from utils.solver.solver import MatrixVectorSolver


class PronyPolynomialComplexExponentialEstimator(
        PronyComplexExponentialEstimator):
    """Complex exponential estimator using the polynomial method."""

    def __init__(
        self,
        samples: Samples,
        fs: float,
        solver_cls: MatrixVectorSolver = LeastSquaresMatrixVectorSolver
    ) -> None:
        super().__init__(samples, fs)
        self.solver_cls = solver_cls

    def _solve_for_roots(self, num_exponentials: int) -> np.ndarray:
        """Solves for the roots of the characteristic polynomial.

        Args:
            num_exponentials: Number of complex exponentials.

        Returns:
            The roots of the characteristic polynomial.
        """
        # Solve for the homogeneous linear difference equation coefficients.
        A = scipy.linalg.hankel(self.samples[:-num_exponentials],
                                self.samples[-num_exponentials - 1:-1])
        b = -self.samples[num_exponentials:]
        solver = self.solver_cls(A, b)
        tap_coefficients = solver.solution

        # Find the roots of the characteristic polynomial.
        roots = np.polynomial.polynomial.polyroots(
            np.concatenate((tap_coefficients, [1])))
        return roots
