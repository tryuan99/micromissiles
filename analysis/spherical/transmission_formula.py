"""Transmission formula for spherical near-field measurements.

The notation and equation numbers follow J. E. Hansen (ed.), "Spherical
Near-Field Antenna Measurements", IET Electromagnetic Waves Series 26, 1988.
"""

import numpy as np

from analysis.spherical.probe_response import ProbeResponseConstants
from analysis.spherical.spherical_measurement import SphericalMeasurement
from analysis.spherical.spherical_wave_coefficients import \
    SphericalWaveCoefficients
from analysis.spherical.wigner_d import WignerD


class TransmissionFormula:
    """Transmission formula with probe correction for a mu = +/-1 probe.

    The transmission formula in eqn (4.40) with an input signal of v = 1 is
        w(chi, theta, phi) = sum_{s, mu, n, m} T_{smn} exp(im phi)
            d^n_{mu m}(theta) exp(i mu chi) P_{s mu n}(kA).

    Attributes:
        probe_response: Probe response constants P_{s mu n}(kA).
    """

    # Azimuthal probe indices mu corresponding to mu index 0 and 1.
    PROBE_MU = ProbeResponseConstants.PROBE_MU

    # Relative singular value cutoff of the least squares solution.
    LEAST_SQUARES_RCOND = 1e-2

    def __init__(self, probe_coefficients: SphericalWaveCoefficients, kA: float,
                 max_degree: int) -> None:
        """Initializes the transmission formula.

        Args:
            probe_coefficients: Probe transmitting coefficients in the probe's
                own coordinate system.
            kA: Wavenumber times the measurement distance.
            max_degree: Maximum degree N of the test antenna.
        """
        self.probe_response = ProbeResponseConstants(probe_coefficients, kA,
                                                     max_degree)

    @property
    def max_degree(self) -> int:
        """Maximum degree N of the test antenna."""
        return self.probe_response.max_degree

    def evaluate(
        self,
        coefficients: SphericalWaveCoefficients,
        theta: np.ndarray,
        phi: np.ndarray,
        chi: np.ndarray,
    ) -> np.ndarray:
        """Evaluates the received signal.

        Args:
            coefficients: Test antenna transmitting coefficients T_{smn}.
            theta: Theta with shape (num_theta,).
            phi: Phi with shape (num_theta, num_phi).
            chi: Probe rotation angle with shape (num_theta,).

        Returns:
            The received signal with shape (num_theta, num_phi).
        """
        coefficients = coefficients.resize(self.max_degree)
        m = np.arange(-self.max_degree, self.max_degree + 1)
        w = np.zeros(phi.shape, dtype=np.complex128)
        for mu_index, mu in enumerate(self.PROBE_MU):
            # Sum over s with shape (N + 1, 2N + 1).
            q = np.einsum("snm,sn->nm", coefficients.values,
                          self.probe_response.values[:, mu_index])
            d = WignerD.table(self.max_degree, mu, theta)
            # w_{mu m}(theta) with shape (num_theta, 2N + 1).
            w_mu_m = np.einsum("nm,nmi->im", q, d)
            w += np.exp(1j * mu * chi)[:, np.newaxis] * np.einsum(
                "im,ijm->ij",
                w_mu_m,
                np.exp(
                    1j * m[np.newaxis, np.newaxis, :] * phi[:, :, np.newaxis]),
            )
        return w

    def solve(self,
              measurement: SphericalMeasurement) -> SphericalWaveCoefficients:
        """Solves for the test antenna transmitting coefficients.

        The transmission formula is solved with the three-step procedure in
        Section 4.3: a solution in chi, a DFT in phi, and an integration in
        theta, followed by the solution of eqns (4.53-4.54) for each (m, n).
        With a measurement mask, it is solved by least squares instead.

        Args:
            measurement: Spherical near-field measurement.

        Returns:
            The test antenna transmitting coefficients T_{smn}.
        """
        if measurement.mask is not None:
            return self._solve_least_squares(measurement)
        w_mu = self._solve_chi(measurement.w, measurement.chi)
        w_mu_m = self._solve_phi(w_mu, measurement.phi)
        w_n_mu_m = self._solve_theta(w_mu_m, measurement.theta)

        coefficients = SphericalWaveCoefficients.zeros(self.max_degree)
        for n in range(1, self.max_degree + 1):
            # Matrix with shape (2 [mu], 2 [s]).
            matrix = self.probe_response.values[:, :, n].T
            m = np.arange(-n, n + 1) + self.max_degree
            coefficients.values[:, n,
                                m] = np.linalg.solve(matrix, w_n_mu_m[:, n, m])
        return coefficients

    def relative_residual(self, measurement: SphericalMeasurement,
                          coefficients: SphericalWaveCoefficients) -> float:
        """Computes the relative residual of the transmission formula.

        Args:
            measurement: Spherical near-field measurement.
            coefficients: Test antenna transmitting coefficients T_{smn}.

        Returns:
            ||w - w_model|| / ||w||, where w_model is the received signal
            predicted by the transmission formula.
        """
        w_model = np.stack([
            self.evaluate(coefficients, measurement.theta, measurement.phi, chi)
            for chi in measurement.chi
        ])
        mask = (measurement.mask if measurement.mask is not None else np.ones(
            measurement.w.shape, dtype=bool))
        return (np.linalg.norm((measurement.w - w_model)[mask]) /
                np.linalg.norm(measurement.w[mask]))

    def _solve_least_squares(
            self,
            measurement: SphericalMeasurement) -> SphericalWaveCoefficients:
        """Solves eqn (4.40) for the measured samples by truncated least squares.

        Args:
            measurement: Spherical near-field measurement with a mask.

        Returns:
            The test antenna transmitting coefficients T_{smn}.
        """
        matrix = np.concatenate([
            self._design_matrix(measurement.theta, measurement.phi, chi)[mask]
            for chi, mask in zip(measurement.chi, measurement.mask)
        ])
        solution, *_ = np.linalg.lstsq(matrix,
                                       measurement.w[measurement.mask],
                                       rcond=self.LEAST_SQUARES_RCOND)
        return SphericalWaveCoefficients(
            solution.reshape(2, self.max_degree + 1, 2 * self.max_degree + 1))

    def _design_matrix(self, theta: np.ndarray, phi: np.ndarray,
                       chi: np.ndarray) -> np.ndarray:
        """Computes the received signal for each unit coefficient T_{smn}.

        Args:
            theta: Theta with shape (num_theta,).
            phi: Phi with shape (num_theta, num_phi).
            chi: Probe rotation angle with shape (num_theta,).

        Returns:
            The received signal with shape
            (num_theta, num_phi, 2 * (N + 1) * (2N + 1)), where the last axis
            is ordered as the flattened coefficient array.
        """
        m = np.arange(-self.max_degree, self.max_degree + 1)
        azimuthal = np.exp(1j * m[np.newaxis, np.newaxis, :] *
                           phi[:, :, np.newaxis])
        matrix = np.zeros(
            (*phi.shape, 2, self.max_degree + 1, 2 * self.max_degree + 1),
            dtype=np.complex128)
        for mu_index, mu in enumerate(self.PROBE_MU):
            d = WignerD.table(self.max_degree, mu, theta)
            matrix += np.einsum("i,sn,nmi,ijm->ijsnm", np.exp(1j * mu * chi),
                                self.probe_response.values[:, mu_index], d,
                                azimuthal)
        return matrix.reshape(*phi.shape, -1)

    def _solve_chi(self, w: np.ndarray, chi: np.ndarray) -> np.ndarray:
        """Solves for w_mu(A, theta, phi) from the two probe polarizations.

        See eqns (4.63-4.66).

        Args:
            w: Received signal with shape (2, num_theta, num_phi).
            chi: Probe rotation angle with shape (2, num_theta).

        Returns:
            w_mu with shape (2, num_theta, num_phi), where index 0 and 1 along
            the first axis correspond to mu = -1 and mu = +1, respectively.

        Raises:
            ValueError: If the two probe polarizations are parallel.
        """
        # Matrix with shape (num_theta, 2, 2) mapping (w_-1, w_1) onto the
        # signals received with both probe polarizations.
        matrix = np.exp(1j * self.PROBE_MU[np.newaxis, np.newaxis, :] *
                        chi.T[:, :, np.newaxis])
        if np.any(np.abs(np.linalg.det(matrix)) < 1e-6):
            raise ValueError("The two probe polarizations must not differ by "
                             "0 or 180 degrees.")
        w_mu = np.linalg.solve(matrix[:, np.newaxis, :, :],
                               w.transpose(1, 2, 0)[..., np.newaxis])
        return w_mu[..., 0].transpose(2, 0, 1)

    def _solve_phi(self, w_mu: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """Computes the phi integral in eqn (4.67) with the DFT.

        Args:
            w_mu: w_mu(A, theta, phi) with shape (2, num_theta, num_phi).
            phi: Equispaced phi in radians with shape (num_theta, num_phi).

        Returns:
            w_{mu m}(A, theta) with shape (2, num_theta, 2N + 1).

        Raises:
            ValueError: If there are too few phi samples.
        """
        num_phi = phi.shape[1]
        if num_phi < 2 * self.max_degree + 1:
            raise ValueError(f"At least {2 * self.max_degree + 1} roll "
                             f"samples are required for N = "
                             f"{self.max_degree}, but there are only "
                             f"{num_phi}.")
        m = np.arange(-self.max_degree, self.max_degree + 1)
        exponentials = np.exp(-1j * m[np.newaxis, np.newaxis, :] *
                              phi[:, :, np.newaxis])
        return np.einsum("uij,ijm->uim", w_mu, exponentials) / num_phi

    def _solve_theta(self, w_mu_m: np.ndarray, theta: np.ndarray) -> np.ndarray:
        """Computes the theta integral in eqn (4.55).

        The data is extended to 0 <= theta < 2pi using eqn (4.72), expanded
        into a Fourier series with the DFT in eqn (4.77), and integrated with
        eqn (4.75).

        Args:
            w_mu_m: w_{mu m}(A, theta) with shape (2, num_theta, 2N + 1).
            theta: Equispaced theta in radians from 0 to pi inclusive.

        Returns:
            w^n_{mu m}(A) with shape (2, N + 1, 2N + 1).

        Raises:
            ValueError: If theta is not sampled correctly.
        """
        num_intervals = len(theta) - 1
        if not np.allclose(theta, np.linspace(0, np.pi, len(theta))):
            raise ValueError("The yaw must be sampled equispaced from 0 to 180 "
                             "degrees inclusive.")
        if num_intervals < self.max_degree + 1:
            raise ValueError(f"At least {self.max_degree + 1} yaw intervals "
                             f"are required for N = {self.max_degree}, but "
                             f"there are only {num_intervals}.")

        m = np.arange(-self.max_degree, self.max_degree + 1)
        # Parity of (mu - m) with shape (2, 2N + 1).
        parity = (-1.0)**(self.PROBE_MU[:, np.newaxis] - m[np.newaxis, :])

        # Extended data with shape (2, 2 * num_intervals, 2N + 1).
        extended = np.concatenate(
            (
                w_mu_m,
                parity[:, np.newaxis, :] * w_mu_m[:, num_intervals - 1:0:-1, :],
            ),
            axis=1,
        )
        extended_theta = np.arange(2 * num_intervals) * np.pi / num_intervals

        # Fourier coefficients b_l^{mu m} with shape (2, 2N + 1, 2N + 1).
        l = m
        b = np.einsum(
            "uim,il->ulm",
            extended,
            np.exp(-1j * extended_theta[:, np.newaxis] * l[np.newaxis, :]),
        ) / (2 * num_intervals)

        # K(m') = sum_l G(l - m') b_l with shape (2, 2N + 1, 2N + 1).
        kernel = self._theta_integral_kernel(l[np.newaxis, :] -
                                             m[:, np.newaxis])
        k = np.einsum("pl,ulm->upm", kernel, b)

        w_n_mu_m = np.zeros((2, self.max_degree + 1, 2 * self.max_degree + 1),
                            dtype=np.complex128)
        for n in range(1, self.max_degree + 1):
            m_prime = np.arange(-n, n + 1)
            # Deltas Delta^n_{m' m} = d^n_{m' m}(pi / 2); see eqn (A2.13).
            deltas = WignerD.evaluate(n, m_prime[:, np.newaxis],
                                      m_prime[np.newaxis, :], np.pi / 2)
            for mu_index, mu in enumerate(self.PROBE_MU):
                k_n = k[mu_index,
                        m_prime + self.max_degree][:, m_prime + self.max_degree]
                w_n_mu_m[mu_index, n, m_prime + self.max_degree] = (
                    (2 * n + 1) / 2 * (1j)**(mu - m_prime) *
                    np.einsum("p,pm,pm->m", deltas[:, mu + n], deltas, k_n))
        return w_n_mu_m

    @staticmethod
    def _theta_integral_kernel(l: np.ndarray) -> np.ndarray:
        """Computes G(l) = integral of exp(il theta) sin(theta) over [0, pi].

        See eqn (4.76).

        Args:
            l: Integer arguments.

        Returns:
            The values of G(l).
        """
        l = np.asarray(l)
        kernel = np.zeros(l.shape, dtype=np.complex128)
        even = l % 2 == 0
        kernel[even] = 2 / (1 - l[even]**2)
        kernel[l == 1] = 1j * np.pi / 2
        kernel[l == -1] = -1j * np.pi / 2
        return kernel
