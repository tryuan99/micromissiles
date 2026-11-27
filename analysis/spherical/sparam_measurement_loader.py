"""Loads the S2P files of a spherical near-field measurement."""

import re
from pathlib import Path

import numpy as np

from analysis.spherical.measurement_loader import MeasurementLoader
from analysis.spherical.positioner_geometry import PositionerGeometry
from utils.devices.vna_calibration import VnaCalibration
from utils.network.sparam_viewer import SParamViewer


class SParamMeasurementLoader(MeasurementLoader):
    """Loads the S2P files of a spherical near-field measurement.

    Each probe polarization is stored in its own directory, and the S2P files
    are named {data_prefix}_yaw{yaw}deg_roll{roll}deg.s2p. The yaw may be
    negative. Samples beyond the measured yaws, e.g., behind the test antenna if
    the yaw is only swept over +/-90 degrees, are set to zero.

    Attributes:
        data_prefix: Data file prefix.
    """

    def __init__(
        self,
        data_dirs: list[str],
        data_prefix: str,
        geometry: PositionerGeometry,
        distance: float,
        probe_angles: list[float],
        sparam: tuple[int, int] = (2, 1),
        calibration: VnaCalibration | None = None,
    ) -> None:
        """Initializes the loader.

        Args:
            data_dirs: Data directories, one for each probe polarization.
            data_prefix: Data file prefix.
            geometry: Positioner geometry.
            distance: Measurement distance in meters.
            probe_angles: Probe polarization angles from vertical in degrees,
                one for each data directory.
            sparam: S-parameter indices (i, j) of the transmission coefficient.
            calibration: Optional VNA calibration applied to the transmission
                coefficient.

        Raises:
            ValueError: If the inputs do not describe a valid measurement.
        """
        super().__init__(
            data_dirs,
            geometry,
            distance,
            probe_angles,
            sparam,
            calibration,
        )
        self.data_prefix = data_prefix

    def _load_polarization(
        self,
        data_source: str,
        frequencies: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Loads the raw transmission coefficient from one data directory.

        Args:
            data_source: Data directory.
            frequencies: Frequencies in Hz.

        Returns:
            A 3-tuple consisting of the transmission coefficient with shape
            (num_frequencies, num_yaws, num_rolls), the yaws in degrees in
            ascending order, and the rolls in degrees in ascending order.

        Raises:
            ValueError: If the S2P files are missing or do not form a grid.
        """
        pattern = re.compile(rf"{re.escape(self.data_prefix)}"
                             r"_yaw(-?\d+(?:\.\d+)?)deg"
                             r"_roll(-?\d+(?:\.\d+)?)deg\.s2p")
        data_paths: dict[tuple[float, float], Path] = {}
        for data_path in Path(data_source).iterdir():
            match = pattern.fullmatch(data_path.name)
            if match is not None:
                data_paths[float(match[1]), float(match[2])] = data_path
        if not data_paths:
            raise ValueError(f"No S2P files were found in {data_source}.")
        yaws = np.unique([yaw for yaw, _ in data_paths])
        rolls = np.unique([roll for _, roll in data_paths])
        if len(data_paths) != len(yaws) * len(rolls):
            raise ValueError("The yaw and the roll must form a grid.")

        transmission = np.zeros(
            (len(frequencies), len(yaws), len(rolls)),
            dtype=np.complex128,
        )
        for (yaw, roll), data_path in data_paths.items():
            sparam_data = SParamViewer(str(data_path))
            indices = np.abs(sparam_data.frequency()[:, np.newaxis] -
                             frequencies).argmin(axis=0)
            transmission[
                :,
                np.searchsorted(yaws, yaw),
                np.searchsorted(rolls, roll),
            ] = sparam_data.s(*self.sparam)[indices]
        return transmission, yaws, rolls
