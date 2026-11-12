"""Translation coefficients and probe response constants.

The notation and equation numbers follow J. E. Hansen (ed.), "Spherical
Near-Field Antenna Measurements", IET Electromagnetic Waves Series 26, 1988.
"""

import numpy as np

from analysis.spherical.spherical_wave_coefficients import \
    SphericalWaveCoefficients
from analysis.spherical.wigner_d import WignerD


class TranslationCoefficients:
    """Translation coefficients C^{sn(3)}_{sigma mu nu}(kA) for mu = +/-1.

    The coefficients for mu = 1 are computed with eqn (A3.19), and the
    coefficients for mu = -1 follow from eqn (A3.21).

    Attributes:
        values: Array of shape (2, 2, 2, N + 1, Nprobe + 1), where entry
            [s - 1, sigma - 1, mu index, n, nu] contains
            C^{sn(3)}_{sigma mu nu}(kA) and mu index 0 and 1 correspond to
            mu = -1 and mu = +1, respectively.
    """

    def __init__(self, kA: float, max_degree: int,
                 probe_max_degree: int) -> None:
        """Computes the translation coefficients.

        Args:
            kA: Wavenumber times the measurement distance.
            max_degree: Maximum degree N of the test antenna.
            probe_max_degree: Maximum degree of the probe.
        """
        hankel = self.spherical_hankel1(max_degree + probe_max_degree, kA)
        self.values = np.zeros(
            (2, 2, 2, max_degree + 1, probe_max_degree + 1),
            dtype=np.complex128,
        )
        for n in range(1, max_degree + 1):
            for nu in range(1, probe_max_degree + 1):
                p = np.arange(abs(n - nu), n + nu + 1, 2)
                log_binomials = (self._log_central_binomial(-n + nu + p) +
                                 self._log_central_binomial(n - nu + p) +
                                 self._log_central_binomial(n + nu - p) -
                                 self._log_central_binomial(n + nu + p))
                common_terms = (np.exp(log_binomials) * (1j)**(-p) *
                                (2 * p + 1) * hankel[p])
                l = n * (n + 1) + nu * (nu + 1) - p * (p + 1)
                same_sum = np.sum(l**2 / (n + nu + p + 1) * common_terms)
                cross_sum = np.sum(2j * kA * l / (n + nu + p + 1) *
                                   common_terms)
                prefactor = (0.25 * (1j)**(n - nu) * np.sqrt(2 * n + 1) /
                             (n * (n + 1)) * np.sqrt(2 * nu + 1) / (nu *
                                                                    (nu + 1)))
                for s in range(2):
                    for sigma in range(2):
                        value = prefactor * (same_sum
                                             if s == sigma else cross_sum)
                        self.values[s, sigma, 1, n, nu] = value
                        self.values[s, sigma, 0, n,
                                    nu] = (-1)**(s + sigma) * value

    @staticmethod
    def spherical_hankel1(max_degree: int, x: float) -> np.ndarray:
        """Computes the spherical Hankel functions of the first kind.

        The upward recurrence relation in eqn (A1.7) is stable for h^(1)_n(x).

        Args:
            max_degree: Maximum degree.
            x: Positive argument.

        Returns:
            An array of h^(1)_n(x) for n = 0, ..., max_degree.
        """
        hankel = np.zeros(max(max_degree + 1, 2), dtype=np.complex128)
        hankel[0] = -1j * np.exp(1j * x) / x
        hankel[1] = np.exp(1j * x) / x * (-1 - 1j / x)
        for n in range(1, max_degree):
            hankel[n + 1] = (2 * n + 1) / x * hankel[n] - hankel[n - 1]
        return hankel[:max_degree + 1]

    @staticmethod
    def _log_central_binomial(two_k: np.ndarray) -> np.ndarray:
        """Computes log(binomial(2k, k)).

        Args:
            two_k: Even arguments 2k.

        Returns:
            The logarithm of the central binomial coefficients.
        """
        log_factorials = WignerD.log_factorials(int(np.max(two_k)))
        return log_factorials[two_k] - 2 * log_factorials[two_k // 2]


class ProbeResponseConstants:
    """Probe response constants P_{s mu n}(kA) for mu = +/-1.

    See eqn (3.26) or eqn (4.39). Only the probe receiving coefficients with
    mu = +/-1 contribute.

    Attributes:
        values: Array of shape (2, 2, N + 1), where entry [s - 1, mu index, n]
            contains P_{s mu n}(kA) and mu index 0 and 1 correspond to mu = -1
            and mu = +1, respectively.
    """

    # Azimuthal probe indices mu corresponding to mu index 0 and 1.
    PROBE_MU = np.array([-1, 1])

    def __init__(self, probe_coefficients: SphericalWaveCoefficients, kA: float,
                 max_degree: int) -> None:
        """Computes the probe response constants.

        Args:
            probe_coefficients: Probe transmitting coefficients in the probe's
                own coordinate system.
            kA: Wavenumber times the measurement distance.
            max_degree: Maximum degree N of the test antenna.
        """
        receiving_coefficients = (
            probe_coefficients.probe_receiving_coefficients())
        probe_max_degree = receiving_coefficients.max_degree
        translation = TranslationCoefficients(kA, max_degree, probe_max_degree)
        # Receiving coefficients R^p_{sigma mu nu} with shape (sigma, mu, nu).
        receiving = receiving_coefficients.values[:, :, self.PROBE_MU +
                                                  probe_max_degree].transpose(
                                                      0, 2, 1)
        self.values = 0.5 * np.einsum("sjunv,juv->sun", translation.values,
                                      receiving)

    @property
    def max_degree(self) -> int:
        """Maximum degree N of the test antenna."""
        return self.values.shape[2] - 1
