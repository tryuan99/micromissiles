"""Calibrates the probe horn from a spherical near-field scan of an identical
horn.

The test antenna is a second horn identical to the probe horn. Both horns are
assumed to be reciprocal, so the probe receiving coefficients follow from the
test antenna transmitting coefficients. The transmission formula is solved
iteratively as in Section 3.2.5 of J. E. Hansen (ed.), "Spherical Near-Field
Antenna Measurements", 1988, starting from a Huygens source as the probe.

The horn coefficients are saved in the horn's own coordinate system, which has
its boresight along +z and its electric field polarized along x at boresight.
"""

import numpy as np
from absl import app, flags, logging

import utils.visualization.mpl_config
from analysis.antenna.marlin.common import RadiationPatternSlice
from analysis.spherical.radiation_pattern_plotter import RadiationPatternPlotter
from analysis.spherical.spherical_measurement import (
    CsvSphericalMeasurementLoader, PositionerGeometry, SphericalMeasurement,
    SphericalMeasurementLoader)
from analysis.spherical.spherical_wave_coefficients import \
    SphericalWaveCoefficients
from analysis.spherical.transmission_formula import TransmissionFormula

FLAGS = flags.FLAGS


class IdenticalHornCalibrator:
    """Calibrates a probe horn by measuring an identical horn.

    Each iteration performs the following steps:
        1. Compute the probe response from the current estimate of the horn
           coefficients.
        2. Solve the transmission formula for the test horn coefficients.
        3. Rotate the solution into the horn's own coordinate system, and update
           the estimate of the horn coefficients.

    Since the received signal is proportional to the product of the probe and
    the test horn coefficients, the horn coefficients are found up to a sign.
    The absolute scale is preserved, so the realized gain of the horn is
    correct if the VNA is calibrated at the horn ports.

    Attributes:
        test_horn_rotation: Rotation in radians about the boresight from the
            test antenna coordinate system to the test horn's own coordinate
            system.
        max_iterations: Maximum number of iterations.
        tolerance: Relative change in the horn coefficients to stop.
    """

    # Relaxation factor for updating the horn coefficients. An error that the
    # iteration maps onto lambda times itself is reduced by
    # 1 - RELAXATION_FACTOR * (1 - lambda) per iteration. The probe correction
    # results in lambda close to 0 or close to -1, so a relaxation factor of 2/3
    # reduces both errors by a factor of 3 per iteration.
    RELAXATION_FACTOR = 2 / 3

    def __init__(self, test_horn_angle: float, max_iterations: int,
                 tolerance: float) -> None:
        """Initializes the calibrator.

        Args:
            test_horn_angle: Polarization angle of the test horn from vertical
                in radians at zero roll.
            max_iterations: Maximum number of iterations.
            tolerance: Relative change in the horn coefficients to stop.
        """
        self.test_horn_rotation = np.pi / 2 + test_horn_angle
        self.max_iterations = max_iterations
        self.tolerance = tolerance

    def calibrate(
        self,
        measurement: SphericalMeasurement,
        max_degree: int,
    ) -> tuple[SphericalWaveCoefficients, SphericalWaveCoefficients,
               TransmissionFormula]:
        """Calibrates the horn at a single frequency.

        Args:
            measurement: Spherical near-field measurement of the test horn.
            max_degree: Maximum degree N of the spherical wave expansion.

        Returns:
            A 3-tuple consisting of the horn coefficients in the horn's own
            coordinate system, the test horn coefficients in the test antenna
            coordinate system, and the transmission formula with the final
            probe.
        """
        horn_coefficients = SphericalWaveCoefficients.huygens_source(max_degree)
        for iteration in range(self.max_iterations):
            transmission_formula = TransmissionFormula(horn_coefficients,
                                                       measurement.kA,
                                                       max_degree)
            test_coefficients = transmission_formula.solve(measurement)
            updated_horn_coefficients = self._update(
                horn_coefficients,
                test_coefficients.rotate_about_z(self.test_horn_rotation),
            )
            change = (np.linalg.norm(updated_horn_coefficients.values -
                                     horn_coefficients.values) /
                      np.linalg.norm(updated_horn_coefficients.values))
            horn_coefficients = updated_horn_coefficients
            logging.info("Iteration %d: relative change = %.3e.", iteration,
                         change)
            if change < self.tolerance:
                break

        # Solve again with the final probe, so that the test horn coefficients
        # are consistent with the horn coefficients.
        transmission_formula = TransmissionFormula(horn_coefficients,
                                                   measurement.kA, max_degree)
        test_coefficients = transmission_formula.solve(measurement)
        return horn_coefficients, test_coefficients, transmission_formula

    def _update(
        self,
        horn_coefficients: SphericalWaveCoefficients,
        solved_coefficients: SphericalWaveCoefficients,
    ) -> SphericalWaveCoefficients:
        """Updates the estimate of the horn coefficients.

        If the current estimate is c * T for the true coefficients T, the
        solved coefficients are approximately T / c. The scale factor c is
        estimated in the least squares sense, and the two estimates of T are
        combined with a relaxation factor.

        The relaxation is needed because an error in the balance between the
        probe modes mu = +1 and mu = -1 is mostly compensated by the opposite
        error in the test horn modes m = +1 and m = -1. Without relaxation, this
        error would flip its sign at every iteration without decaying.

        Args:
            horn_coefficients: Current estimate of the horn coefficients.
            solved_coefficients: Solved test horn coefficients in the horn's own
                coordinate system.

        Returns:
            The updated estimate of the horn coefficients.
        """
        current = horn_coefficients.values
        solved = solved_coefficients.values
        scale = np.sqrt(np.vdot(solved, current) / np.vdot(solved, solved))
        updated = ((1 - self.RELAXATION_FACTOR) * current / scale +
                   self.RELAXATION_FACTOR * scale * solved)
        # Resolve the sign ambiguity by staying close to the current estimate.
        if np.real(np.vdot(current, updated)) < 0:
            updated *= -1
        return SphericalWaveCoefficients(updated)


def main(argv):
    """Calibrates the probe horn and saves its coefficients.

    Args:
        argv: Command-line arguments.
    """
    assert len(argv) == 1

    frequencies = np.array(FLAGS.frequencies)
    geometry = PositionerGeometry(int(FLAGS.yaw_direction),
                                  int(FLAGS.roll_direction))
    if FLAGS.data_csv:
        loader = CsvSphericalMeasurementLoader(
            FLAGS.data_csv,
            FLAGS.probe_angles[0],
            FLAGS.yaw_step,
            FLAGS.roll_step,
            geometry,
            FLAGS.distance,
        )
    else:
        loader = SphericalMeasurementLoader(
            FLAGS.data_dirs,
            FLAGS.data_prefix,
            FLAGS.probe_angles,
            FLAGS.yaw_step,
            FLAGS.roll_step,
            geometry,
            FLAGS.distance,
            (int(FLAGS.sparam[1]), int(FLAGS.sparam[2])),
        )
    calibrator = IdenticalHornCalibrator(
        np.deg2rad(FLAGS.test_horn_angle),
        FLAGS.max_iterations,
        FLAGS.tolerance,
    )

    horn_coefficients_per_frequency = []
    test_coefficients_per_frequency = []
    for measurement in loader.load(frequencies):
        max_degree = (FLAGS.max_degree if FLAGS.max_degree is not None else
                      SphericalWaveCoefficients.max_degree_for_radius(
                          measurement.wavenumber, FLAGS.min_sphere_radius))
        logging.info("Frequency: %.6f GHz, kA = %.2f, N = %d.",
                     measurement.frequency / 1e9, measurement.kA, max_degree)

        horn_coefficients, test_coefficients, transmission_formula = (
            calibrator.calibrate(measurement, max_degree))
        logging.info(
            "Relative residual = %.3e, boresight realized gain = %.2f dBi, "
            "radiated/available power = %.3f.",
            transmission_formula.relative_residual(measurement,
                                                   test_coefficients),
            10 * np.log10(
                horn_coefficients.realized_gain(np.array([0]), np.array([0
                                                                        ]))[0]),
            horn_coefficients.total_power(),
        )
        horn_coefficients_per_frequency.append(horn_coefficients)
        test_coefficients_per_frequency.append(test_coefficients)

    SphericalWaveCoefficients.save(
        FLAGS.output,
        frequencies,
        horn_coefficients_per_frequency,
        distance=FLAGS.distance,
    )
    logging.info("Saved the probe coefficients to %s.", FLAGS.output)

    plotter = RadiationPatternPlotter(
        RadiationPatternSlice(FLAGS.slice),
        FLAGS.polarization == "vertical",
    )
    plotter.plot(test_coefficients_per_frequency, FLAGS.labels,
                 "Calibration horn")


if __name__ == "__main__":
    flags.DEFINE_multi_string(
        "data_dirs", None, "Data directories, one for each probe polarization.")
    flags.DEFINE_string(
        "data_csv", None,
        "CSV file with Azimuth, Roll, Power, and Phase columns for the first "
        "probe angle at one frequency.")
    flags.DEFINE_string("data_prefix", "antenna_sweep", "Data file prefix.")
    flags.DEFINE_multi_float(
        "probe_angles", [0, 90],
        "Probe polarization angles from vertical in degrees, one for each data "
        "directory. Only the first angle is used with --data_csv. Positive "
        "angles are clockwise when looking from the test antenna toward the "
        "probe.")
    flags.DEFINE_float(
        "test_horn_angle", 0,
        "Polarization angle of the test horn from vertical in degrees at zero "
        "roll. Positive angles are clockwise when looking from the test "
        "antenna toward the probe.")
    flags.DEFINE_float(
        "yaw_step",
        None,
        "Yaw step in degrees. The yaw is swept from 0 to 180 degrees.",
        lower_bound=0.0,
    )
    flags.DEFINE_float(
        "roll_step",
        None,
        "Roll step in degrees. The roll is swept from 0 to 360 degrees.",
        lower_bound=0.0,
    )
    flags.DEFINE_enum(
        "yaw_direction", "1", ["1", "-1"],
        "+1 if positive yaw is counterclockwise when viewed from above.")
    flags.DEFINE_enum(
        "roll_direction", "1", ["1", "-1"],
        "+1 if positive roll is clockwise when looking from the test antenna "
        "toward the probe.")
    flags.DEFINE_float(
        "distance",
        None,
        "Distance in meters from the intersection of the yaw and the roll axes "
        "to the origin of the probe horn's coordinate system.",
        lower_bound=0.0,
    )
    flags.DEFINE_float(
        "min_sphere_radius",
        None,
        "Radius in meters of the minimum sphere enclosing the horn centered at "
        "the intersection of the yaw and the roll axes.",
        lower_bound=0.0,
    )
    flags.DEFINE_integer(
        "max_degree",
        None,
        "Maximum degree N of the spherical wave expansion.",
        lower_bound=1,
    )
    flags.DEFINE_multi_float("frequencies", None, "Frequencies in Hz.")
    flags.DEFINE_multi_string("labels", None, "Labels for the plot.")
    flags.DEFINE_enum("sparam", "s21", ["s21", "s12"],
                      "Transmission S-parameter.")
    flags.DEFINE_integer("max_iterations", 50, "Maximum number of iterations.")
    flags.DEFINE_float("tolerance", 1e-8,
                       "Relative change in the horn coefficients to stop.")
    flags.DEFINE_string("output", None,
                        "Output NPZ file for the probe coefficients.")
    flags.DEFINE_enum("slice", RadiationPatternSlice.AZIMUTH.value, [
        radiation_pattern_slice.value
        for radiation_pattern_slice in RadiationPatternSlice
    ], "Radiation pattern slice.")
    flags.DEFINE_enum("polarization", "vertical", ["vertical", "horizontal"],
                      "Co-polarization of the plot.")
    flags.mark_flags_as_required([
        "yaw_step",
        "roll_step",
        "distance",
        "frequencies",
        "output",
    ])
    flags.mark_flags_as_mutual_exclusive(
        ["data_dirs", "data_csv"],
        required=True,
    )
    flags.mark_flags_as_mutual_exclusive(
        ["min_sphere_radius", "max_degree"],
        required=True,
    )

    app.run(main)
