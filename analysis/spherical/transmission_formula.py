"""Transmission formula for spherical near-field measurements.

The notation and equation numbers follow J. E. Hansen (ed.), "Spherical
Near-Field Antenna Measurements", IET Electromagnetic Waves Series 26, 1988.
"""

import numpy as np

from analysis.spherical.probe_response_constants import ProbeResponseConstants
from analysis.spherical.rotation_coefficients import RotationCoefficients
from analysis.spherical.spherical_measurement import SphericalMeasurement
from analysis.spherical.spherical_wave_coefficients import \
    SphericalWaveCoefficients
from utils import constants


class TransmissionFormula:
    """Transmission formula with probe correction for a mu = +/-1 probe.

    The transmission formula in eqn (4.40) with an input signal of v = 1 is
        w(chi, theta, phi) = sum_{s, mu, n, m} T_{smn} exp(im phi)
            d^n_{mu m}(theta) exp(i mu chi) P_{s mu n}(kA).

    Attributes:
        max_degree: Maximum degree N of the test antenna.
        m: Azimuthal indices m from -N to N.
        probe_response: Probe response constants P_{s mu n}(kA) with shape
            (2, 2, N + 1).
    """

    # Minimum angle in degrees between the two probe polarizations.
    MIN_POLARIZATION_SEPARATION = 20

    def __init__(
        self,
        max_degree: int,
        kA: float,
        probe_coefficients: SphericalWaveCoefficients,
    ) -> None:
        """Initializes the transmission formula.

        Args:
            max_degree: Maximum degree N of the test antenna.
            kA: Wavenumber times the measurement distance.
            probe_coefficients: Probe transmitting coefficients in the probe's
                own coordinate system.
        """
        self.max_degree = max_degree
        self.m = np.arange(-max_degree, max_degree + 1)
        self.probe_response = ProbeResponseConstants.evaluate(
            probe_coefficients,
            kA,
            max_degree,
        )

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
            phi: Equispaced phi in radians from 0 up to 2pi with shape
                (num_theta, num_phi).
            chi: Probe rotation angle with shape (num_theta,).

        Returns:
            The received signal with shape (num_theta, num_phi).

        Raises:
            ValueError: If phi is not sampled correctly.
        """
        coefficients = coefficients.resize(self.max_degree)
        w_m = np.zeros((len(theta), len(self.m)), dtype=np.complex128)
        for mu_index, mu in enumerate(ProbeResponseConstants.PROBE_MU):
            # Sum over s with shape (N + 1, 2N + 1).
            q = np.einsum(
                "snm,sn->nm",
                coefficients.values,
                self.probe_response[:, mu_index],
            )
            d = RotationCoefficients.evaluate_all(self.max_degree, mu, theta)
            # w_{mu m}(theta) with shape (num_theta, 2N + 1).
            w_mu_m = np.einsum("nm,nmi->im", q, d)
            w_m += np.exp(1j * mu * chi)[:, np.newaxis] * w_mu_m
        return self._sum_phi(w_m, phi)

    def solve(
        self,
        measurement: SphericalMeasurement,
    ) -> SphericalWaveCoefficients:
        """Solves for the test antenna transmitting coefficients.

        The transmission formula is solved with the three-step procedure in
        Section 4.3: a solution in chi, a DFT in phi, and an integration in
        theta, followed by the solution of eqns (4.53-4.54) for each (m, n).

        Args:
            measurement: Spherical near-field measurement.

        Returns:
            The test antenna transmitting coefficients T_{smn}.
        """
        w_mu = self._solve_chi(measurement.w, measurement.chi)
        w_mu_m = self._solve_phi(w_mu, measurement.phi)
        w_n_mu_m = self._solve_theta(w_mu_m, measurement.theta)

        coefficients = SphericalWaveCoefficients.zeros(self.max_degree)
        # Matrices with shape (N, 2 [mu], 2 [s]).
        matrices = self.probe_response[:, :, 1:].transpose(2, 1, 0)
        coefficients.values[:, 1:] = np.linalg.solve(
            matrices, w_n_mu_m[:, 1:].transpose(1, 0, 2)).transpose(1, 0, 2)
        return coefficients

    def relative_residual(
        self,
        measurement: SphericalMeasurement,
        coefficients: SphericalWaveCoefficients,
    ) -> float:
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
        return (np.linalg.norm(measurement.w - w_model) /
                np.linalg.norm(measurement.w))

    def _sum_phi(self, w_m: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """Sums the Fourier series in phi with the inverse FFT.

        Args:
            w_m: Fourier coefficients with shape (num_theta, 2N + 1).
            phi: Equispaced phi in radians from 0 up to 2pi with shape
                (num_theta, num_phi).

        Returns:
            sum_m w_m exp(im phi) with shape (num_theta, num_phi).

        Raises:
            ValueError: If phi is not sampled correctly.
        """
        self._check_phi(phi)
        num_phi = phi.shape[1]
        spectrum = np.zeros(phi.shape, dtype=np.complex128)
        spectrum[:, self.m % num_phi] = w_m
        return np.fft.ifft(spectrum, axis=-1) * num_phi

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
            ValueError: If the two probe polarizations are nearly parallel.
        """
        if np.any(
                np.abs(np.sin(chi[1] - chi[0])) < np.sin(
                    constants.deg2rad(self.MIN_POLARIZATION_SEPARATION))):
            raise ValueError(f"The two probe polarizations must be at least "
                             f"{self.MIN_POLARIZATION_SEPARATION} degrees from "
                             f"parallel.")
        # Matrix with shape (num_theta, 2, 2) mapping (w_-1, w_1) onto the
        # signals received with both probe polarizations.
        matrix = np.exp(1j * chi.T[:, :, np.newaxis] *
                        ProbeResponseConstants.PROBE_MU)
        return np.linalg.solve(matrix, w.transpose(1, 0, 2)).transpose(1, 0, 2)

    def _solve_phi(self, w_mu: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """Computes the phi integral in eqn (4.67) with the FFT.

        Args:
            w_mu: w_mu(A, theta, phi) with shape (2, num_theta, num_phi).
            phi: Equispaced phi in radians from 0 up to 2pi with shape
                (num_theta, num_phi).

        Returns:
            w_{mu m}(A, theta) with shape (2, num_theta, 2N + 1).

        Raises:
            ValueError: If phi is not sampled correctly.
        """
        self._check_phi(phi)
        num_phi = phi.shape[1]
        return np.fft.fft(w_mu, axis=-1)[..., self.m % num_phi] / num_phi

    def _solve_theta(self, w_mu_m: np.ndarray, theta: np.ndarray) -> np.ndarray:
        """Computes the theta integral in eqn (4.55).

        The data is extended to 0 <= theta < 2pi using eqn (4.72), expanded into
        a Fourier series with the FFT in eqn (4.77), and integrated with
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
            raise ValueError(f"N = {self.max_degree} requires at least "
                             f"{self.max_degree + 1} yaw intervals, but there "
                             f"are {num_intervals}.")

        mu = ProbeResponseConstants.PROBE_MU
        # Parity of (mu - m) with shape (2, 2N + 1).
        parity = (-1.0)**(mu[:, np.newaxis] - self.m)

        # Extended data with shape (2, 2 * num_intervals, 2N + 1).
        reflected = parity[:, np.newaxis] * w_mu_m[:, num_intervals - 1:0:-1]
        extended = np.concatenate((w_mu_m, reflected), axis=1)

        # Fourier coefficients b_l^{mu m} with shape (2, 2N + 1, 2N + 1).
        b = (np.fft.fft(extended, axis=1)[:, self.m % (2 * num_intervals)] /
             (2 * num_intervals))

        # K(m') = sum_l G(l - m') b_l with shape (2, 2N + 1, 2N + 1).
        kernel = self._theta_integral_kernel(self.m - self.m[:, np.newaxis])
        k = np.einsum("pl,ulm->upm", kernel, b)

        w_n_mu_m = np.zeros((2, self.max_degree + 1, len(self.m)),
                            dtype=np.complex128)
        for n in range(1, self.max_degree + 1):
            m_prime = np.arange(-n, n + 1)
            indices = m_prime + self.max_degree
            # Deltas Delta^n_{m' m} = d^n_{m' m}(pi / 2); see eqn (A2.13).
            deltas = RotationCoefficients.evaluate(n, m_prime[:, np.newaxis],
                                                   m_prime, np.pi / 2)
            w_n_mu_m[:, n, indices] = (
                (2 * n + 1) / 2 * (1j)**(mu[:, np.newaxis] - m_prime) *
                np.einsum("pu,pm,upm->um", deltas[:, mu + n], deltas,
                          k[:, indices[:, np.newaxis], indices]))
        return w_n_mu_m

    def _check_phi(self, phi: np.ndarray) -> None:
        """Checks that phi is equispaced from 0 up to 2pi with enough samples.

        Args:
            phi: Phi in radians with shape (num_theta, num_phi).

        Raises:
            ValueError: If phi is not sampled correctly.
        """
        num_phi = phi.shape[1]
        if num_phi < len(self.m):
            raise ValueError(f"N = {self.max_degree} requires at least "
                             f"{len(self.m)} roll samples, but there are "
                             f"{num_phi}.")
        if not np.allclose(phi, np.arange(num_phi) * 2 * np.pi / num_phi):
            raise ValueError("The roll must be sampled equispaced from 0 up to "
                             "360 degrees.")

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
