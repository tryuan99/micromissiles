"""The matrix pencil method complex exponential estimator estimates the
parameters of complex exponentials using the matrix pencil method.

See https://bmcbioinformatics.biomedcentral.com/articles/10.1186/s12859-018-2473-y
and https://ieeexplore.ieee.org/document/370583.
"""

import numpy as np
import scipy.linalg

from simulation.estimator.prony.prony_complex_exponential_estimator import \
    PronyComplexExponentialEstimator
from simulation.radar.components.samples import Samples


class PronyMpmComplexExponentialEstimator(PronyComplexExponentialEstimator):
    """Complex exponential estimator using the matrix pencil method."""

    def __init__(self, samples: Samples, fs: float) -> None:
        super().__init__(samples, fs)

    def _solve_for_roots(self, num_exponentials: int) -> np.ndarray:
        """Solves for the roots of the characteristic polynomial.

        Args:
            num_exponentials: Number of complex exponentials.

        Returns:
            The roots of the characteristic polynomial.
        """
        # Form the Hankel matrix of samples.
        Y = scipy.linalg.hankel(self.samples[:-num_exponentials],
                                self.samples[-num_exponentials - 1:])
        Y1 = Y[:, :-1]
        Y2 = Y[:, 1:]

        # The roots of the characteristic polynomial are the eigenvalues of the
        # matrix pencil (Y2, Y1). Equivalently, they are the eigenvalues of
        # Y1^+Y2, where + denotes the Moore-Penrose pseudoinverse.
        roots = np.linalg.eigvals(np.linalg.pinv(Y1) @ Y2)
        return roots


class PronyMpmNoiseComplexExponentialEstimator(PronyComplexExponentialEstimator
                                              ):
    """Complex exponential estimator using the matrix pencil method.

    According to https://ieeexplore.ieee.org/document/370583, this method
    provides minimum variance in the presence of noise.
    """

    def __init__(self, samples: Samples, fs: float) -> None:
        super().__init__(samples, fs)

    def _solve_for_roots(self, num_exponentials: int) -> np.ndarray:
        """Solves for the roots of the characteristic polynomial.

        Args:
            num_exponentials: Number of complex exponentials.

        Returns:
            The roots of the characteristic polynomial.
        """
        # Form the Hankel matrix of samples.
        Y = scipy.linalg.hankel(self.samples[:-num_exponentials],
                                self.samples[-num_exponentials - 1:])

        # Filter for just the dominant right singular vectors.
        _, _, Vh = np.linalg.svd(Y)
        Vh_filtered = Vh[:num_exponentials]
        V1 = Vh_filtered[:, :-1]
        V2 = Vh_filtered[:, 1:]

        # The roots of the characteristic polynomial are the eigenvalues of the
        # matrix pencil (V2, V1). Equivalently, they are the eigenvalues of
        # V1^+V2, where + denotes the Moore-Penrose pseudoinverse.
        roots = np.linalg.eigvals(np.linalg.pinv(V1) @ V2)
        return roots
