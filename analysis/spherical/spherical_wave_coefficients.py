"""Spherical wave coefficients of an antenna.

The notation and equation numbers follow J. E. Hansen (ed.), "Spherical
Near-Field Antenna Measurements", IET Electromagnetic Waves Series 26, 1988.
The time convention is exp(-iwt).
"""

from typing import Self

import numpy as np

from analysis.spherical.wigner_d import WignerD


class SphericalWaveCoefficients:
    """Spherical wave coefficients T_{smn} of an antenna.

    The coefficients are stored in an array of shape (2, N + 1, 2N + 1), where
    the coefficient of mode (s, m, n) is located at [s - 1, n, m + N] and N is
    the maximum degree. Entries with n = 0 or |m| > n are unused and zero.

    With an input signal of v = 1, sum |T_{smn}|^2 is the ratio of the radiated
    power to the available input power, and the realized gain is |K|^2, where
    K is the far-field pattern; see eqns (A1.3) and (2.208).

    Attributes:
        values: Coefficient array with shape (2, N + 1, 2N + 1).
    """

    def __init__(self, values: np.ndarray) -> None:
        """Initializes the spherical wave coefficients.

        Args:
            values: Coefficient array with shape (2, N + 1, 2N + 1).
        """
        self.values = np.asarray(values, dtype=np.complex128)

    @classmethod
    def zeros(cls, max_degree: int) -> Self:
        """Creates coefficients that are all zero.

        Args:
            max_degree: Maximum degree N.

        Returns:
            The zero coefficients.
        """
        return cls(
            np.zeros((2, max_degree + 1, 2 * max_degree + 1),
                     dtype=np.complex128))

    @classmethod
    def huygens_source(cls, max_degree: int = 1) -> Self:
        """Creates the coefficients of an x-polarized Huygens source.

        The Huygens source radiates toward +z with no back radiation and has a
        gain of 3. It is a good initial approximation of a probe with
        mu = +/-1 only; see Section 3.2.5.

        Args:
            max_degree: Maximum degree N of the returned coefficients.

        Returns:
            The Huygens source coefficients normalized to unit power.
        """
        coefficients = cls.zeros(max_degree)
        coefficients.values[0, 1, max_degree + 1] = 1
        coefficients.values[1, 1, max_degree + 1] = 1
        coefficients.values[0, 1, max_degree - 1] = 1
        coefficients.values[1, 1, max_degree - 1] = -1
        return cls(coefficients.values / np.sqrt(coefficients.total_power()))

    @staticmethod
    def max_degree_for_radius(k: float, radius: float) -> int:
        """Computes the maximum degree N of the spherical wave expansion.

        See Section 4.3.2: N = kr0 + 10, where r0 is the radius of the minimum
        sphere enclosing the antenna.

        Args:
            k: Wavenumber in rad/m.
            radius: Minimum sphere radius in meters.

        Returns:
            The maximum degree N.
        """
        return int(np.ceil(k * radius)) + 10

    @staticmethod
    def save(path: str, frequencies: np.ndarray, coefficients: list[Self],
             **metadata: float) -> None:
        """Saves the coefficients at multiple frequencies to an NPZ file.

        Args:
            path: Output NPZ file.
            frequencies: Frequencies in Hz.
            coefficients: Coefficients for each frequency.
            **metadata: Additional scalar values to save.
        """
        max_degrees = [
            frequency_coefficients.max_degree
            for frequency_coefficients in coefficients
        ]
        np.savez(
            path,
            frequencies=frequencies,
            coefficients=np.stack([
                frequency_coefficients.resize(max(max_degrees)).values
                for frequency_coefficients in coefficients
            ]),
            max_degrees=np.array(max_degrees),
            **metadata,
        )

    @classmethod
    def load(cls, path: str) -> tuple[np.ndarray, list[Self], dict]:
        """Loads the coefficients at multiple frequencies from an NPZ file.

        Args:
            path: NPZ file written by save().

        Returns:
            A 3-tuple consisting of the frequencies in Hz, the coefficients for
            each frequency, and a dictionary of the additional saved values.
        """
        data = np.load(path)
        coefficients = [
            cls(values).resize(max_degree) for values, max_degree in zip(
                data["coefficients"], data["max_degrees"])
        ]
        metadata = {
            key: data[key]
            for key in data.files
            if key not in ("frequencies", "coefficients", "max_degrees")
        }
        return data["frequencies"], coefficients, metadata

    @property
    def max_degree(self) -> int:
        """Maximum degree N."""
        return self.values.shape[1] - 1

    def total_power(self) -> float:
        """Computes the ratio of the radiated to the available input power.

        Returns:
            The sum of |T_{smn}|^2.
        """
        return np.sum(np.abs(self.values)**2)

    def resize(self, max_degree: int) -> Self:
        """Truncates or zero-pads the coefficients to the given maximum degree.

        Args:
            max_degree: New maximum degree N.

        Returns:
            The resized coefficients.
        """
        resized = SphericalWaveCoefficients.zeros(max_degree)
        common_degree = min(max_degree, self.max_degree)
        m = np.arange(-common_degree, common_degree + 1)
        resized.values[:, :common_degree + 1,
                       m + max_degree] = self.values[:, :common_degree + 1,
                                                     m + self.max_degree]
        return resized

    def rotate_about_z(self, angle: float) -> Self:
        """Expresses the coefficients in a coordinate system rotated about z.

        If the new coordinate system is obtained by rotating the original one
        by the given angle about the z-axis, then by eqn (A2.2), the
        coefficients in the new coordinate system are
        T'_{smn} = T_{smn} exp(im angle).

        Args:
            angle: Rotation angle in radians.

        Returns:
            The coefficients in the rotated coordinate system.
        """
        m = np.arange(-self.max_degree, self.max_degree + 1)
        return SphericalWaveCoefficients(
            self.values * np.exp(1j * m * angle)[np.newaxis, np.newaxis, :])

    def probe_receiving_coefficients(self) -> Self:
        """Computes the receiving coefficients R^p of this antenna as a probe.

        The transmitting coefficients are defined in the antenna's own
        coordinate system with the boresight along +z. In the transmission
        formula, the probe coordinate system has its z'-axis pointing away from
        the test antenna, so the probe is rotated by pi about its y-axis.
        Combining eqn (A2.2) with d^n_{mu m}(pi) = (-1)^(n + mu) delta_{mu, -m}
        and the reciprocity relation in eqn (3.21) yields
        R^p_{sigma mu nu} = (-1)^nu T_{sigma mu nu}.

        The probe is assumed to be reciprocal and polarized along its x-axis.

        Returns:
            The probe receiving coefficients in the primed probe coordinate
            system.
        """
        nu = np.arange(self.max_degree + 1)
        return SphericalWaveCoefficients(
            self.values * ((-1.0)**nu)[np.newaxis, :, np.newaxis])

    def far_field(self, theta: np.ndarray,
                  phi: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Computes the far-field pattern K(theta, phi) = sum T_{smn} K_{smn}.

        The far-field pattern functions are evaluated with eqns (A2.20-A2.23).

        Args:
            theta: Theta in radians with shape (num_points,).
            phi: Phi in radians with shape (num_points,).

        Returns:
            A 2-tuple consisting of the theta and phi components of the
            far-field pattern, each with shape (num_points,).
        """
        theta = np.asarray(theta, dtype=np.float64)
        phi = np.asarray(phi, dtype=np.float64)
        m = np.arange(-self.max_degree, self.max_degree + 1)
        n = np.arange(self.max_degree + 1)
        d_plus = WignerD.table(self.max_degree, 1, theta)
        d_minus = WignerD.table(self.max_degree, -1, theta)
        d_sum = d_plus + d_minus
        d_difference = d_plus - d_minus
        # Degree-dependent factors with shape (N + 1, 1, 1).
        theta_factor = (-np.sqrt(2 * n + 1) / (2 * (1j)**n))[:, np.newaxis,
                                                             np.newaxis]
        phi_factor = (np.sqrt(2 * n + 1) / (2 * (1j)**(n + 1)))[:, np.newaxis,
                                                                np.newaxis]
        # Azimuthal factor with shape (2N + 1, num_points).
        azimuthal = np.exp(1j * m[:, np.newaxis] * phi[np.newaxis, :])
        k_theta = (np.einsum("nm,nmi,mi->i", self.values[0],
                             theta_factor * d_sum, azimuthal) +
                   np.einsum("nm,nmi,mi->i", self.values[1],
                             theta_factor * d_difference, azimuthal))
        k_phi = (np.einsum("nm,nmi,mi->i", self.values[0],
                           phi_factor * d_difference, azimuthal) +
                 np.einsum("nm,nmi,mi->i", self.values[1], phi_factor * d_sum,
                           azimuthal))
        return k_theta, k_phi

    def realized_gain(self, theta: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """Computes the realized gain |K(theta, phi)|^2.

        Args:
            theta: Theta in radians with shape (num_points,).
            phi: Phi in radians with shape (num_points,).

        Returns:
            The realized gain with shape (num_points,).
        """
        k_theta, k_phi = self.far_field(theta, phi)
        return np.abs(k_theta)**2 + np.abs(k_phi)**2
