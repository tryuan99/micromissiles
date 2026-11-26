"""Rotation coefficients of spherical waves.

The notation and equation numbers follow J. E. Hansen (ed.), "Spherical
Near-Field Antenna Measurements", IET Electromagnetic Waves Series 26, 1988.
"""

import functools

import numpy as np


class RotationCoefficients:
    """Rotation coefficients d^n_{mu m}(theta) of spherical waves.

    The rotation coefficients are also known as the Wigner small-d functions.

    See Appendix A2.
    """

    @staticmethod
    def evaluate(
        n: int,
        mu: np.ndarray,
        m: np.ndarray,
        theta: np.ndarray,
    ) -> np.ndarray:
        """Evaluates the rotation coefficient d^n_{mu m}(theta).

        The rotation coefficient is evaluated using the Jacobi polynomial
        representation in eqn (A2.5) and the symmetries in eqns (A2.8-A2.9).

        Args:
            n: Degree.
            mu: Azimuthal index mu. Broadcast against m and theta.
            m: Azimuthal index m. Broadcast against mu and theta.
            theta: Angle in radians. Broadcast against mu and m.

        Returns:
            The rotation coefficient with the broadcast shape of the inputs.
        """
        mu, m, theta = np.broadcast_arrays(
            np.asarray(mu, dtype=int),
            np.asarray(m, dtype=int),
            np.asarray(theta, dtype=np.float64),
        )
        valid = (np.abs(mu) <= n) & (np.abs(m) <= n)

        # Map (mu, m) onto (a, b) with a >= |b|.
        parity = np.where((mu + m) % 2 == 0, 1.0, -1.0)
        case_1 = mu >= np.abs(m)
        case_2 = ~case_1 & (m >= np.abs(mu))
        case_3 = ~case_1 & ~case_2 & (-mu >= np.abs(m))
        a = np.select([case_1, case_2, case_3], [mu, m, -mu], -m)
        b = np.select([case_1, case_2, case_3], [m, mu, -m], -mu)
        sign = np.select([case_1, case_2, case_3], [1.0, parity, parity], 1.0)
        a = np.where(valid, a, 0)
        b = np.where(valid, b, 0)

        alpha = (a - b).astype(np.float64)
        beta = (a + b).astype(np.float64)
        degree = n - a

        log_factorials = RotationCoefficients.log_factorials(2 * n + 1)
        log_prefactor = 0.5 * (log_factorials[n + a] + log_factorials[n - a] -
                               log_factorials[n + b] - log_factorials[n - b])
        prefactor = (np.exp(log_prefactor) * np.cos(theta / 2)**(a + b) *
                     np.sin(theta / 2)**(a - b))

        # Evaluate the Jacobi polynomial P^{(alpha, beta)}_{degree}(cos(theta))
        # with the three-term recurrence relation.
        x = np.cos(theta)
        jacobi_previous = np.ones_like(x)
        jacobi = (alpha + 1) + (alpha + beta + 2) * (x - 1) / 2
        result = np.where(degree == 0, jacobi_previous, 0.0)
        result = np.where(degree == 1, jacobi, result)
        for j in range(2, int(np.max(degree, initial=0)) + 1):
            c = 2 * j + alpha + beta
            jacobi_next = (
                (c - 1) * (c * (c - 2) * x + alpha**2 - beta**2) * jacobi - 2 *
                (j + alpha - 1) *
                (j + beta - 1) * c * jacobi_previous) / (2 * j *
                                                         (j + alpha + beta) *
                                                         (c - 2))
            jacobi_previous, jacobi = jacobi, jacobi_next
            result = np.where(degree == j, jacobi, result)
        return np.where(valid, sign * prefactor * result, 0.0)

    @staticmethod
    def evaluate_all(max_degree: int, mu: int, theta: np.ndarray) -> np.ndarray:
        """Evaluates d^n_{mu m}(theta) for all degrees n and orders m.

        Args:
            max_degree: Maximum degree N.
            mu: Azimuthal index mu.
            theta: Angles in radians.

        Returns:
            An array of shape (N + 1, 2N + 1, len(theta)), where entry
            [n, m + N] contains d^n_{mu m}(theta).
        """
        theta = np.asarray(theta, dtype=np.float64)
        m = np.arange(-max_degree, max_degree + 1)
        values = np.zeros((max_degree + 1, 2 * max_degree + 1, len(theta)))
        for n in range(1, max_degree + 1):
            values[n] = RotationCoefficients.evaluate(n, mu, m[:, np.newaxis],
                                                      theta[np.newaxis, :])
        return values

    @staticmethod
    @functools.cache
    def log_factorials(n: int) -> np.ndarray:
        """Tabulates log(k!) for k = 0, ..., n.

        Args:
            n: Maximum argument.

        Returns:
            An array of log(k!) with shape (n + 1,).
        """
        return np.concatenate(([0], np.cumsum(np.log(np.arange(1, n + 1)))))
