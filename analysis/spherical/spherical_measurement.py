"""Spherical near-field measurements with a yaw-over-roll positioner.

The test antenna sits on a roll positioner (about the test antenna boresight)
that is mounted on top of a yaw positioner (about the vertical axis). The probe
is fixed and looks at the test antenna along the horizontal line through the
intersection of the roll and the yaw axes.

The chamber coordinate system has its origin at the intersection of the roll
and the yaw axes. Z points from the test antenna toward the probe, Y points up,
and X = Y x Z points to the left when looking from behind the test antenna
toward the probe. The test antenna coordinate system coincides with the chamber
coordinate system when the yaw and the roll are both zero, so the test antenna
boresight is +z and +y is up.

Positive yaw is a right-hand rotation about +Y (up), and positive roll is a
right-hand rotation about the test antenna boresight. The probe polarization
angle is measured from vertical (+Y) and is positive for a right-hand rotation
about +Z, i.e., clockwise when looking from the test antenna toward the probe.

With these conventions, the probe coordinate system relative to the test
antenna coordinate system is given by the Euler angles (see Appendix A2 of
J. E. Hansen (ed.), "Spherical Near-Field Antenna Measurements", 1988)
    theta = yaw,
    phi = pi - roll,
    chi = probe polarization angle - pi / 2.
"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from utils.network.sparam_viewer import SParamViewer

# Speed of light in m/s.
SPEED_OF_LIGHT = 299792458


@dataclass
class SphericalMeasurement:
    """Spherical near-field measurement at a single frequency.

    Attributes:
        frequency: Frequency in Hz.
        distance: Distance in meters from the test antenna coordinate origin to
            the probe coordinate origin.
        w: Received signal with shape (2, num_theta, num_phi) for the two
            probe polarizations.
        theta: Equispaced theta from 0 to pi inclusive with shape (num_theta,).
        phi: Equispaced phi covering 2pi with shape (num_theta, num_phi).
        chi: Probe rotation angle with shape (2, num_theta).
        mask: Boolean array with the same shape as w that is true for the
            measured samples, or None if all samples are measured.
    """
    frequency: float
    distance: float
    w: np.ndarray
    theta: np.ndarray
    phi: np.ndarray
    chi: np.ndarray
    mask: np.ndarray | None = None

    @property
    def wavenumber(self) -> float:
        """Free-space wavenumber k in rad/m."""
        return 2 * np.pi * self.frequency / SPEED_OF_LIGHT

    @property
    def kA(self) -> float:
        """Wavenumber times the measurement distance."""
        return self.wavenumber * self.distance


class PositionerGeometry:
    """Converts the positioner angles into the Euler angles of the probe.

    Attributes:
        yaw_direction: +1 if positive yaw is a right-hand rotation about up.
        roll_direction: +1 if positive roll is a right-hand rotation about the
            test antenna boresight.
    """

    def __init__(self, yaw_direction: int = 1, roll_direction: int = 1) -> None:
        """Initializes the positioner geometry.

        Args:
            yaw_direction: +1 if positive yaw is a right-hand rotation about up.
            roll_direction: +1 if positive roll is a right-hand rotation about
                the test antenna boresight.
        """
        self.yaw_direction = yaw_direction
        self.roll_direction = roll_direction

    def euler_angles(
        self,
        yaws: np.ndarray,
        rolls: np.ndarray,
        probe_angle: float,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Computes the Euler angles of the probe for every yaw and roll.

        Args:
            yaws: Yaw angles in radians with shape (num_yaws,).
            rolls: Roll angles in radians with shape (num_rolls,).
            probe_angle: Probe polarization angle from vertical in radians.

        Returns:
            A 3-tuple consisting of theta with shape (num_yaws,), phi with
            shape (num_yaws, num_rolls), and chi with shape (num_yaws,).
        """
        theta = self.yaw_direction * np.asarray(yaws, dtype=np.float64)
        phi = np.pi - self.roll_direction * np.asarray(rolls, dtype=np.float64)
        phi = np.broadcast_to(phi, (len(theta), len(phi))).copy()
        chi = np.full(len(theta), probe_angle - np.pi / 2)

        # A negative theta is equivalent to (-theta, phi + pi, chi - pi) since
        # R_y(-theta) = R_z(pi) R_y(theta) R_z(-pi).
        negative = theta < 0
        theta[negative] *= -1
        phi[negative] += np.pi
        chi[negative] -= np.pi
        return theta, np.mod(phi, 2 * np.pi), chi


class SphericalMeasurementLoader:
    """Loads the S2P files of a spherical near-field measurement.

    The yaw is swept from 0 to 180 degrees inclusive, and the roll is swept
    from 0 degrees up to but excluding 360 degrees. Each probe polarization is
    stored in its own directory, and the S2P files are named
    {data_prefix}_yaw{yaw}deg_roll{roll}deg.s2p.

    Attributes:
        data_dirs: Data directories, one for each probe polarization.
        data_prefix: Data file prefix.
        probe_angles: Probe polarization angles from vertical in degrees.
        yaws: Yaw angles in degrees.
        rolls: Roll angles in degrees.
        geometry: Positioner geometry.
        distance: Measurement distance in meters.
        sparam: S-parameter indices (i, j) of the transmission coefficient.
    """

    def __init__(
            self,
            data_dirs: list[str],
            data_prefix: str,
            probe_angles: list[float],
            yaw_step: float,
            roll_step: float,
            geometry: PositionerGeometry,
            distance: float,
            sparam: tuple[int, int] = (2, 1),
    ) -> None:
        """Initializes the loader.

        Args:
            data_dirs: Data directories, one for each probe polarization.
            data_prefix: Data file prefix.
            probe_angles: Probe polarization angles from vertical in degrees,
                one for each data directory.
            yaw_step: Yaw step in degrees.
            roll_step: Roll step in degrees.
            geometry: Positioner geometry.
            distance: Measurement distance in meters.
            sparam: S-parameter indices (i, j) of the transmission coefficient.

        Raises:
            ValueError: If the inputs do not describe a valid measurement.
        """
        if len(data_dirs) != 2 or len(probe_angles) != 2:
            raise ValueError("Exactly two data directories and two probe "
                             "angles are required.")
        if not np.isclose(180 / yaw_step, np.round(180 / yaw_step)):
            raise ValueError("The yaw step must divide 180 degrees.")
        if not np.isclose(360 / roll_step, np.round(360 / roll_step)):
            raise ValueError("The roll step must divide 360 degrees.")
        self.data_dirs = data_dirs
        self.data_prefix = data_prefix
        self.probe_angles = probe_angles
        self.yaws = np.linspace(0, 180, int(np.round(180 / yaw_step)) + 1)
        self.rolls = np.linspace(0, 360,
                                 int(np.round(360 / roll_step)) + 1)[:-1]
        self.geometry = geometry
        self.distance = distance
        self.sparam = sparam

    def load(self, frequencies: np.ndarray) -> list[SphericalMeasurement]:
        """Loads the measurements at the given frequencies.

        Args:
            frequencies: Frequencies in Hz.

        Returns:
            The measurement at each frequency.
        """
        # Received signal with shape (num_frequencies, 2, num_yaws, num_rolls).
        w = np.stack(
            [
                self._load_directory(data_dir, frequencies)
                for data_dir in self.data_dirs
            ],
            axis=1,
        )
        chis = []
        for probe_angle in self.probe_angles:
            theta, phi, chi = self.geometry.euler_angles(
                np.deg2rad(self.yaws),
                np.deg2rad(self.rolls),
                np.deg2rad(probe_angle),
            )
            chis.append(chi)
        chi = np.stack(chis)
        # Sort theta in ascending order in case the yaw direction is negative.
        order = np.argsort(theta)
        return [
            SphericalMeasurement(
                frequency=frequency,
                distance=self.distance,
                w=w[frequency_index][:, order],
                theta=theta[order],
                phi=phi[order],
                chi=chi[:, order],
            ) for frequency_index, frequency in enumerate(frequencies)
        ]

    def _load_directory(self, data_dir: str,
                        frequencies: np.ndarray) -> np.ndarray:
        """Loads the transmission coefficient at every yaw and roll.

        Args:
            data_dir: Data directory.
            frequencies: Frequencies in Hz.

        Returns:
            An array of shape (num_frequencies, num_yaws, num_rolls) containing
            the complex transmission coefficient.
        """
        data_dir_path = Path(data_dir)
        data = np.zeros((len(frequencies), len(self.yaws), len(self.rolls)),
                        dtype=np.complex128)
        for yaw_index, yaw in enumerate(self.yaws):
            yaw_str = f"{yaw:.6f}".rstrip("0").rstrip(".")
            for roll_index, roll in enumerate(self.rolls):
                roll_str = f"{roll:.6f}".rstrip("0").rstrip(".")
                data_path = (data_dir_path / f"{self.data_prefix}_yaw{yaw_str}"
                             f"deg_roll{roll_str}deg.s2p")
                sparam_data = SParamViewer(data_path)
                indices = np.abs(sparam_data.frequency()[:, None] -
                                 frequencies).argmin(axis=0)
                data[:, yaw_index,
                     roll_index] = sparam_data.s(*self.sparam)[indices]
        return data


class CsvSphericalMeasurementLoader:
    """Loads a single-frequency, single-polarization measurement from a CSV.

    The columns are Azimuth (yaw) and Roll in degrees, Power in dB, and Phase in
    degrees. Other columns are ignored. Azimuth may be negative. Samples beyond
    the measured azimuths and for the orthogonal probe are masked out.

    Attributes:
        data_path: CSV file.
        probe_angle: Probe polarization angle from vertical in degrees.
        yaw_step: Yaw step in degrees.
        roll_step: Roll step in degrees.
        geometry: Positioner geometry.
        distance: Measurement distance in meters.
    """

    def __init__(
        self,
        data_path: str,
        probe_angle: float,
        yaw_step: float,
        roll_step: float,
        geometry: PositionerGeometry,
        distance: float,
    ) -> None:
        """Initializes the loader.

        Args:
            data_path: CSV file.
            probe_angle: Probe polarization angle from vertical in degrees.
            yaw_step: Yaw step in degrees.
            roll_step: Roll step in degrees.
            geometry: Positioner geometry.
            distance: Measurement distance in meters.

        Raises:
            ValueError: If the inputs do not describe a valid measurement.
        """
        if not np.isclose(180 / yaw_step, np.round(180 / yaw_step)):
            raise ValueError("The yaw step must divide 180 degrees.")
        if not np.isclose(180 / roll_step, np.round(180 / roll_step)):
            raise ValueError("The roll step must divide 180 degrees.")
        self.data_path = data_path
        self.probe_angle = probe_angle
        self.yaw_step = yaw_step
        self.roll_step = roll_step
        self.geometry = geometry
        self.distance = distance

    def load(self, frequencies: np.ndarray) -> list[SphericalMeasurement]:
        """Loads the measurement.

        Args:
            frequencies: Frequency in Hz with shape (1,).

        Returns:
            The measurement at the frequency.

        Raises:
            ValueError: If the grid is incomplete or misaligned.
        """
        if len(frequencies) != 1:
            raise ValueError("A CSV measurement has exactly one frequency.")
        data = np.genfromtxt(self.data_path, delimiter=",", names=True)
        yaws, yaw_indices = np.unique(data["Azimuth"], return_inverse=True)
        rolls, roll_indices = np.unique(data["Roll"], return_inverse=True)
        measured = np.full((len(yaws), len(rolls)), np.nan, dtype=np.complex128)
        measured[yaw_indices,
                 roll_indices] = (10**(data["Power"] / 20) *
                                  np.exp(1j * np.deg2rad(data["Phase"])))
        if np.any(np.isnan(measured)):
            raise ValueError("The azimuth and the roll must form a grid.")

        probe_chi = np.deg2rad(self.probe_angle) - np.pi / 2
        theta, phi, chi = self.geometry.euler_angles(
            np.deg2rad(yaws),
            np.deg2rad(rolls),
            np.deg2rad(self.probe_angle),
        )
        measured *= np.where(np.isclose(chi, probe_chi), 1, -1)[:, np.newaxis]

        num_thetas = int(np.round(180 / self.yaw_step)) + 1
        num_phis = int(np.round(360 / self.roll_step))
        theta_indices = np.round(theta / np.deg2rad(self.yaw_step)).astype(int)
        phi_indices = np.round(phi / np.deg2rad(self.roll_step)).astype(int)
        if (not np.allclose(theta_indices * np.deg2rad(self.yaw_step), theta) or
                not np.allclose(phi_indices * np.deg2rad(self.roll_step), phi)):
            raise ValueError("The azimuth and the roll must be multiples of "
                             "the yaw and the roll steps.")
        theta_indices = np.broadcast_to(theta_indices[:, np.newaxis],
                                        phi_indices.shape)
        phi_indices = np.mod(phi_indices, num_phis)

        w_sum = np.zeros((num_thetas, num_phis), dtype=np.complex128)
        counts = np.zeros((num_thetas, num_phis))
        np.add.at(w_sum, (theta_indices, phi_indices), measured)
        np.add.at(counts, (theta_indices, phi_indices), 1)
        missing = (counts[0] == 0) & (np.roll(counts[0], num_phis // 2) > 0)
        w_sum[0, missing] = -np.roll(w_sum[0], num_phis // 2)[missing]
        counts[0, missing] = np.roll(counts[0], num_phis // 2)[missing]
        max_theta_index = np.max(theta_indices)
        if np.any(counts[:max_theta_index + 1] == 0):
            raise ValueError("The measurement must cover all rolls up to the "
                             "largest measured azimuth.")
        measured_mask = counts > 0
        w = np.divide(w_sum,
                      counts,
                      out=np.zeros_like(w_sum),
                      where=measured_mask)

        return [
            SphericalMeasurement(
                frequency=frequencies[0],
                distance=self.distance,
                w=np.stack((w, np.zeros_like(w))),
                theta=np.linspace(0, np.pi, num_thetas),
                phi=np.broadcast_to(
                    np.arange(num_phis) * 2 * np.pi / num_phis,
                    (num_thetas, num_phis)).copy(),
                chi=np.stack((np.full(num_thetas, probe_chi),
                              np.full(num_thetas, probe_chi + np.pi / 2))),
                mask=np.stack((measured_mask, np.zeros_like(measured_mask))),
            )
        ]
