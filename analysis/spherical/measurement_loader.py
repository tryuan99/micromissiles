"""Interface for loading a spherical near-field measurement."""

from abc import ABC, abstractmethod

import numpy as np

from analysis.spherical.positioner_geometry import PositionerGeometry
from analysis.spherical.spherical_measurement import SphericalMeasurement
from utils import constants
from utils.devices.vna_calibration import VnaCalibration


class MeasurementLoader(ABC):
    """Interface for loading a spherical near-field measurement.

    Attributes:
        data_sources: Data sources, one for each probe polarization.
        geometry: Positioner geometry.
        distance: Measurement distance in meters.
        probe_angles: Probe polarization angles from vertical in degrees.
        sparam: S-parameter indices (i, j) of the transmission coefficient.
        calibration: Optional VNA calibration applied to the transmission
            coefficient.
    """

    def __init__(
        self,
        data_sources: list[str],
        geometry: PositionerGeometry,
        distance: float,
        probe_angles: list[float],
        sparam: tuple[int, int] = (2, 1),
        calibration: VnaCalibration | None = None,
    ) -> None:
        """Initializes the loader.

        Args:
            data_sources: Data sources, one for each probe polarization.
            geometry: Positioner geometry.
            distance: Measurement distance in meters.
            probe_angles: Probe polarization angles from vertical in degrees,
                one for each data source.
            sparam: S-parameter indices (i, j) of the transmission coefficient.
            calibration: Optional VNA calibration applied to the transmission
                coefficient.

        Raises:
            ValueError: If the inputs do not describe a valid measurement.
        """
        if len(probe_angles) != 2:
            raise ValueError("Exactly two probe angles are required.")
        if len(data_sources) != len(probe_angles):
            raise ValueError("One data source is required for each probe "
                             "angle.")
        self.data_sources = data_sources
        self.geometry = geometry
        self.distance = distance
        self.probe_angles = probe_angles
        self.sparam = sparam
        self.calibration = calibration

    def load(
        self,
        frequencies: np.ndarray,
        yaw_step: float,
        roll_step: float,
    ) -> list[SphericalMeasurement]:
        """Loads the measurements at the given frequencies.

        Args:
            frequencies: Frequencies in Hz.
            yaw_step: Yaw step in degrees.
            roll_step: Roll step in degrees.

        Returns:
            The measurement at each frequency.

        Raises:
            ValueError: If the data is not a valid measurement.
        """
        if not np.isclose(180 / yaw_step, np.round(180 / yaw_step)):
            raise ValueError("The yaw step must divide 180 degrees.")
        if not np.isclose(180 / roll_step, np.round(180 / roll_step)):
            raise ValueError("The roll step must divide 180 degrees.")
        num_thetas = int(np.round(180 / yaw_step)) + 1
        num_phis = int(np.round(360 / roll_step))

        w = []
        for data_source in self.data_sources:
            transmission, yaws, rolls = self._load_polarization(
                data_source, frequencies)
            if self.calibration is not None:
                receiver_port, source_port = self.sparam
                transmission = self.calibration.correct_coefficient(
                    frequencies[:, np.newaxis, np.newaxis],
                    transmission,
                    source_port,
                    receiver_port,
                )
            w.append(
                self._to_theta_phi_grid(
                    transmission,
                    yaws,
                    rolls,
                    num_thetas,
                    num_phis,
                ))
        w = np.stack(w, axis=1)

        theta = np.linspace(0, np.pi, num_thetas)
        phi = np.broadcast_to(
            np.arange(num_phis) * 2 * np.pi / num_phis,
            (num_thetas, num_phis),
        )
        chi = np.stack([
            np.full(
                num_thetas,
                PositionerGeometry.probe_chi(constants.deg2rad(probe_angle)),
            ) for probe_angle in self.probe_angles
        ])
        return [
            SphericalMeasurement(
                frequency=frequency,
                distance=self.distance,
                w=w[frequency_index],
                theta=theta.copy(),
                phi=phi.copy(),
                chi=chi.copy(),
            ) for frequency_index, frequency in enumerate(frequencies)
        ]

    @abstractmethod
    def _load_polarization(
        self,
        data_source: str,
        frequencies: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Loads the raw transmission coefficient of one probe polarization.

        Args:
            data_source: Data source of the probe polarization.
            frequencies: Frequencies in Hz.

        Returns:
            A 3-tuple consisting of the transmission coefficient with shape
            (num_frequencies, num_yaws, num_rolls), the yaws in degrees in
            ascending order, and the rolls in degrees in ascending order.

        Raises:
            ValueError: If the data is not a valid measurement.
        """

    def _to_theta_phi_grid(
        self,
        transmission: np.ndarray,
        yaws: np.ndarray,
        rolls: np.ndarray,
        num_thetas: int,
        num_phis: int,
    ) -> np.ndarray:
        """Maps one probe polarization onto the theta and phi grid.

        Args:
            transmission: Transmission coefficient with shape
                (num_frequencies, num_yaws, num_rolls).
            yaws: Yaw angles in degrees, which may be negative.
            rolls: Roll angles in degrees.
            num_thetas: Number of theta samples from 0 to 180 degrees
                inclusive.
            num_phis: Number of phi samples covering 360 degrees.

        Returns:
            The received signal with shape
            (num_frequencies, num_thetas, num_phis), which is zero beyond the
            measured yaws.

        Raises:
            ValueError: If the grid is incomplete or misaligned.
        """
        theta, phi, sign = self.geometry.spherical_angles(
            constants.deg2rad(yaws), constants.deg2rad(rolls))
        transmission = transmission * sign[:, np.newaxis]

        theta_step = np.pi / (num_thetas - 1)
        phi_step = 2 * np.pi / num_phis
        theta_indices = np.round(theta / theta_step).astype(int)
        phi_indices = np.round(phi / phi_step).astype(int)
        if (not np.allclose(theta_indices * theta_step, theta) or
                not np.allclose(phi_indices * phi_step, phi)):
            raise ValueError("The yaw and the roll must be multiples of the "
                             "yaw and the roll steps.")
        theta_indices = np.broadcast_to(
            theta_indices[:, np.newaxis],
            phi_indices.shape,
        )
        phi_indices = np.mod(phi_indices, num_phis)

        w_sum = np.zeros(
            (num_thetas, num_phis, len(transmission)),
            dtype=np.complex128,
        )
        counts = np.zeros((num_thetas, num_phis))
        np.add.at(w_sum, (theta_indices, phi_indices),
                  np.moveaxis(transmission, 0, -1))
        np.add.at(counts, (theta_indices, phi_indices), 1)
        missing = (counts[0] == 0) & (np.roll(counts[0], num_phis // 2) > 0)
        w_sum[0, missing] = -np.roll(w_sum[0], num_phis // 2, axis=0)[missing]
        counts[0, missing] = np.roll(counts[0], num_phis // 2)[missing]
        if np.any(counts[:np.max(theta_indices) + 1] == 0):
            raise ValueError("The measurement must cover all rolls up to the "
                             "largest measured yaw.")
        w = np.divide(
            w_sum,
            counts[..., np.newaxis],
            out=np.zeros_like(w_sum),
            where=counts[..., np.newaxis] > 0,
        )
        return np.moveaxis(w, -1, 0)
