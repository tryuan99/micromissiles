"""Spherical wave coefficients of an antenna.

The notation and equation numbers follow J. E. Hansen (ed.), "Spherical
Near-Field Antenna Measurements", IET Electromagnetic Waves Series 26, 1988. The
time convention is exp(-iwt).
"""

from typing import Self

import numpy as np
import pandas as pd

from analysis.spherical.rotation_coefficients import RotationCoefficients


class SphericalWaveCoefficients:
    """Spherical wave coefficients T_{smn} of an antenna.

    The coefficients are stored in an array of shape (2, N + 1, 2N + 1), where
    the coefficient of mode (s, m, n) is located at [s - 1, n, m + N] and N is
    the maximum degree. Entries with n = 0 or |m| > n are unused and zero.

    With an input signal of v = 1, sum |T_{smn}|^2 is the ratio of the radiated
    power to the available input power, and the realized gain is |K|^2, where K
    is the far-field pattern; see eqns (A1.3) and (2.211).

    Attributes:
        values: Coefficient array with shape (2, N + 1, 2N + 1).
    """

    # Columns of the CSV file containing the spherical wave coefficients.
    CSV_COLUMNS = ("Frequency [Hz]", "s", "m", "n", "Real", "Imaginary")

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
                     dtype=np.complex128),)

    @classmethod
    def huygens_source(cls, max_degree: int = 1) -> Self:
        """Creates the coefficients of an x-polarized Huygens source.

        The Huygens source radiates toward +z with no back radiation and has a
        gain of 3; see Sections 2.3.4 and 2.4.4. It is a good initial
        approximation of a probe with mu = +/-1 only; see Section 3.2.5.

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
    def save(path: str, frequencies: np.ndarray,
             coefficients: list[Self]) -> None:
        """Saves the coefficients at multiple frequencies to a CSV file.

        Each row contains the frequency, the mode indices s, m, and n, and the
        real and imaginary parts of the coefficient T_{smn}.

        Args:
            path: Output CSV file.
            frequencies: Frequencies in Hz.
            coefficients: Coefficients for each frequency.
        """
        rows = []
        for frequency, frequency_coefficients in zip(frequencies, coefficients):
            max_degree = frequency_coefficients.max_degree
            for s in (1, 2):
                for n in range(1, max_degree + 1):
                    for m in range(-n, n + 1):
                        value = frequency_coefficients.values[s - 1, n,
                                                              m + max_degree]
                        rows.append(
                            (frequency, s, m, n, value.real, value.imag))
        df = pd.DataFrame(rows, columns=SphericalWaveCoefficients.CSV_COLUMNS)
        df.to_csv(path, index=False)

    @classmethod
    def load(cls, path: str) -> tuple[np.ndarray, list[Self]]:
        """Loads the coefficients at multiple frequencies from a CSV file.

        Args:
            path: CSV file written by save().

        Returns:
            A 2-tuple consisting of the frequencies in Hz and the coefficients
            for each frequency.
        """
        df = pd.read_csv(path, comment="#", float_precision="round_trip")
        (
            frequency_column,
            s_column,
            m_column,
            n_column,
            real_column,
            imaginary_column,
        ) = cls.CSV_COLUMNS
        frequencies = []
        coefficients = []
        for frequency, frequency_df in df.groupby(frequency_column):
            s = frequency_df[s_column].to_numpy()
            m = frequency_df[m_column].to_numpy()
            n = frequency_df[n_column].to_numpy()
            max_degree = np.max(n)
            frequency_coefficients = cls.zeros(max_degree)
            frequency_coefficients.values[s - 1, n, m + max_degree] = (
                frequency_df[real_column].to_numpy() +
                1j * frequency_df[imaginary_column].to_numpy())
            frequencies.append(frequency)
            coefficients.append(frequency_coefficients)
        return np.array(frequencies), coefficients

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
        resized = type(self).zeros(max_degree)
        common_degree = min(max_degree, self.max_degree)
        m = np.arange(-common_degree, common_degree + 1)
        resized.values[:, :common_degree + 1,
                       m + max_degree] = self.values[:, :common_degree + 1,
                                                     m + self.max_degree]
        return resized

    def rotate_about_z(self, angle: float) -> Self:
        """Expresses the coefficients in a coordinate system rotated about z.

        If the new coordinate system is obtained by rotating the original one by
        the given angle about the z-axis, then by eqn (A2.2), the coefficients
        in the new coordinate system are T'_{smn} = T_{smn} exp(im angle).

        Args:
            angle: Rotation angle in radians.

        Returns:
            The coefficients in the rotated coordinate system.
        """
        m = np.arange(-self.max_degree, self.max_degree + 1)
        return type(self)(self.values *
                          np.exp(1j * m * angle)[np.newaxis, np.newaxis, :])

    def rotate_about_y(self, angle: float) -> Self:
        """Expresses the coefficients in a coordinate system rotated about y.

        If the new coordinate system is obtained by rotating the original one by
        the given angle about the y-axis, then by eqn (A2.2), the coefficients
        in the new coordinate system are
        T'_{s mu n} = sum_m T_{smn} d^n_{mu m}(angle).

        Args:
            angle: Rotation angle in radians.

        Returns:
            The coefficients in the rotated coordinate system.
        """
        m = np.arange(-self.max_degree, self.max_degree + 1)
        rotated = type(self).zeros(self.max_degree)
        for n in range(1, self.max_degree + 1):
            d = RotationCoefficients.evaluate(n, m[:, np.newaxis],
                                              m[np.newaxis, :], angle)
            rotated.values[:, n] = np.einsum("um,sm->su", d, self.values[:, n])
        return rotated

    def receiving_coefficients(self) -> Self:
        """Computes the receiving coefficients of a reciprocal antenna.

        By the reciprocity relation in eqn (3.22), R_{smn} = (-1)^m T_{s,-m,n}.

        Returns:
            The receiving coefficients in the same coordinate system as the
            transmitting coefficients.
        """
        m = np.arange(-self.max_degree, self.max_degree + 1)
        return type(self)(self.values[:, :, ::-1] *
                          ((-1.0)**m)[np.newaxis, np.newaxis, :])

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
        d_plus = RotationCoefficients.evaluate_all(self.max_degree, 1, theta)
        d_minus = RotationCoefficients.evaluate_all(self.max_degree, -1, theta)
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
