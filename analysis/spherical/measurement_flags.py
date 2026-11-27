"""Command-line flags shared by the spherical near-field measurement scripts."""

from absl import flags

from analysis.spherical.csv_measurement_loader import CsvMeasurementLoader
from analysis.spherical.measurement_loader import MeasurementLoader
from analysis.spherical.positioner_geometry import (PositionerGeometry,
                                                    RotationDirection)
from analysis.spherical.radiation_pattern_plotter import (
    Polarization, RadiationPatternPlotter)
from analysis.spherical.sparam_measurement_loader import SParamMeasurementLoader
from analysis.spherical.spherical_measurement import SphericalMeasurement
from analysis.spherical.spherical_wave_coefficients import \
    SphericalWaveCoefficients
from utils.devices.fieldfox_calibration import FieldFoxCalibration

FLAGS = flags.FLAGS


class MeasurementFlags:
    """Command-line flags shared by the spherical measurement scripts."""

    @staticmethod
    def define_flags() -> None:
        """Defines the flags for loading, solving, and plotting."""
        flags.DEFINE_multi_string(
            "data_dirs", None,
            "Data directories, one for each probe polarization.")
        flags.DEFINE_multi_string(
            "data_csvs", None,
            "CSV files from the Keysight OTA Chamber Control software with "
            "Azimuth, Roll, DutPhi, DutTheta, Power, and Phase columns at one "
            "frequency, one for each probe angle.")
        flags.DEFINE_string("data_prefix", "antenna_sweep", "Data file prefix.")
        flags.DEFINE_string(
            "vna_calibration", None,
            "Optional FieldFox state file (.sta) whose user calibration is "
            "applied to the transmission coefficient.")
        flags.DEFINE_multi_float(
            "probe_angles", [0, 90],
            "Probe polarization angles in degrees from the +y-axis (up), "
            "right-handed around the +z-axis (toward the probe), one for each "
            "data directory or CSV file.")
        flags.DEFINE_float(
            "yaw_step",
            None,
            "Yaw step in degrees. The yaw may be negative.",
            lower_bound=0.0,
        )
        flags.DEFINE_float(
            "roll_step",
            None,
            "Roll step in degrees, which must divide 180 degrees.",
            lower_bound=0.0,
        )
        rotation_directions = [
            str(direction.value) for direction in RotationDirection
        ]
        flags.DEFINE_enum(
            "yaw_direction", str(RotationDirection.LEFT_HAND.value),
            rotation_directions,
            "1 if positive yaw is right-handed around the +y-axis (up).")
        flags.DEFINE_enum(
            "roll_direction", str(RotationDirection.LEFT_HAND.value),
            rotation_directions,
            "1 if positive roll is right-handed around the test antenna "
            "boresight.")
        flags.DEFINE_float(
            "distance",
            None,
            "Distance in meters from the intersection of the yaw and the roll "
            "axes to the origin of the probe's coordinate system.",
            lower_bound=0.0,
        )
        flags.DEFINE_float(
            "min_sphere_radius",
            None,
            "Radius in meters of the minimum sphere enclosing the test antenna "
            "centered at the intersection of the yaw and the roll axes.",
            lower_bound=0.0,
        )
        flags.DEFINE_integer(
            "max_degree",
            None,
            "Maximum degree N of the spherical wave expansion.",
            lower_bound=1,
        )
        flags.DEFINE_multi_float("frequencies", None, "Frequencies in Hz.")
        flags.DEFINE_multi_string(
            "labels", None,
            "Plot labels, one for each frequency. Defaults to the frequencies "
            "in GHz.")
        flags.DEFINE_enum("sparam", "s21", ["s21", "s12"],
                          "Transmission S-parameter.")
        flags.DEFINE_enum(
            "polarization",
            Polarization.VERTICAL.value,
            [polarization.value for polarization in Polarization],
            "Polarization of the test antenna.",
        )
        flags.mark_flags_as_required([
            "yaw_step",
            "roll_step",
            "distance",
            "frequencies",
        ])
        flags.mark_flags_as_mutual_exclusive(
            ["data_dirs", "data_csvs"],
            required=True,
        )
        flags.mark_flags_as_mutual_exclusive(
            ["min_sphere_radius", "max_degree"],
            required=True,
        )

    @staticmethod
    def create_loader() -> MeasurementLoader:
        """Creates the measurement loader from the flags.

        Returns:
            The CSV loader if CSV files are given and the S2P loader otherwise.
        """
        geometry = PositionerGeometry(
            RotationDirection(int(FLAGS.yaw_direction)),
            RotationDirection(int(FLAGS.roll_direction)),
        )
        calibration = (FieldFoxCalibration(FLAGS.vna_calibration)
                       if FLAGS.vna_calibration else None)
        sparam = (int(FLAGS.sparam[1]), int(FLAGS.sparam[2]))
        if FLAGS.data_csvs:
            return CsvMeasurementLoader(
                FLAGS.data_csvs,
                geometry,
                FLAGS.distance,
                FLAGS.probe_angles,
                sparam,
                calibration,
            )
        return SParamMeasurementLoader(
            FLAGS.data_dirs,
            FLAGS.data_prefix,
            geometry,
            FLAGS.distance,
            FLAGS.probe_angles,
            sparam,
            calibration,
        )

    @staticmethod
    def max_degree(measurement: SphericalMeasurement) -> int:
        """Determines the maximum degree N of the spherical wave expansion.

        Args:
            measurement: Spherical near-field measurement.

        Returns:
            The maximum degree from the flags or from the minimum sphere radius.
        """
        if FLAGS.max_degree is not None:
            return FLAGS.max_degree
        return SphericalWaveCoefficients.max_degree_for_radius(
            measurement.wavenumber, FLAGS.min_sphere_radius)

    @staticmethod
    def create_plotter() -> RadiationPatternPlotter:
        """Creates the radiation pattern plotter from the flags.

        Returns:
            The radiation pattern plotter.
        """
        return RadiationPatternPlotter(Polarization(FLAGS.polarization))
