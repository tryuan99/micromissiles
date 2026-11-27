"""Loads a single-frequency spherical near-field measurement from CSV files."""

import numpy as np
import pandas as pd

from analysis.spherical.measurement_loader import MeasurementLoader
from analysis.spherical.positioner_geometry import PositionerGeometry
from utils import constants
from utils.devices.vna_calibration import VnaCalibration


class CsvMeasurementLoader(MeasurementLoader):
    """Loads a single-frequency measurement from one CSV per probe polarization.

    The CSV files come from the Keysight OTA Chamber Control software. The
    columns are Azimuth, Roll, DutPhi, and DutTheta in degrees, Power in dB, and
    Phase in degrees, where Azimuth is the yaw. DutPhi and DutTheta are ignored.
    The yaw may be negative. Samples beyond the measured yaws, e.g., behind the
    test antenna if the yaw is only swept over +/-90 degrees, are set to zero.
    """

    def __init__(
        self,
        data_paths: list[str],
        geometry: PositionerGeometry,
        distance: float,
        probe_angles: list[float],
        sparam: tuple[int, int] = (2, 1),
        calibration: VnaCalibration | None = None,
    ) -> None:
        """Initializes the loader.

        Args:
            data_paths: CSV files, one for each probe polarization.
            geometry: Positioner geometry.
            distance: Measurement distance in meters.
            probe_angles: Probe polarization angles from vertical in degrees,
                one for each CSV file.
            sparam: S-parameter indices (i, j) of the transmission coefficient.
            calibration: Optional VNA calibration applied to the transmission
                coefficient.

        Raises:
            ValueError: If the inputs do not describe a valid measurement.
        """
        super().__init__(
            data_paths,
            geometry,
            distance,
            probe_angles,
            sparam,
            calibration,
        )

    def _load_polarization(
        self,
        data_source: str,
        frequencies: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Loads the raw transmission coefficient from one CSV file.

        Args:
            data_source: CSV file.
            frequencies: Frequency in Hz with shape (1,).

        Returns:
            A 3-tuple consisting of the transmission coefficient with shape
            (1, num_yaws, num_rolls), the yaws in degrees in ascending order,
            and the rolls in degrees in ascending order.

        Raises:
            ValueError: If the CSV file is not a valid measurement.
        """
        if len(frequencies) != 1:
            raise ValueError("A CSV measurement has exactly one frequency.")
        df = pd.read_csv(data_source, comment="#")
        (
            azimuth_column,
            roll_column,
            _,
            _,
            power_column,
            phase_column,
        ) = df.columns
        yaws, yaw_indices = np.unique(df[azimuth_column], return_inverse=True)
        rolls, roll_indices = np.unique(df[roll_column], return_inverse=True)
        transmission = np.full(
            (1, len(yaws), len(rolls)),
            np.nan,
            dtype=np.complex128,
        )
        transmission[0, yaw_indices, roll_indices] = (
            constants.db2mag(df[power_column].to_numpy()) *
            np.exp(1j * constants.deg2rad(df[phase_column].to_numpy())))
        if np.any(np.isnan(transmission)):
            raise ValueError("The yaw and the roll must form a grid.")
        return transmission, yaws, rolls
