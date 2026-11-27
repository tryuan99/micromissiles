"""Calibrates the probe from a spherical near-field scan of an identical
antenna.

The probe coefficients are saved in the probe's own coordinate system, which has
its boresight along the +z-axis and its electric field along the +x-axis.
"""

import numpy as np
from absl import app, flags, logging

import utils.visualization.mpl_config
from analysis.spherical.identical_antenna_calibrator import \
    IdenticalAntennaCalibrator
from analysis.spherical.measurement_flags import MeasurementFlags
from analysis.spherical.probe_calibration import ProbeCalibration
from analysis.spherical.spherical_wave_coefficients import \
    SphericalWaveCoefficients
from utils import constants

FLAGS = flags.FLAGS


def main(argv):
    """Calibrates the probe and saves its coefficients.

    Args:
        argv: Command-line arguments.
    """
    assert len(argv) == 1

    frequencies = np.array(FLAGS.frequencies)
    loader = MeasurementFlags.create_loader()
    calibrator = IdenticalAntennaCalibrator(
        constants.deg2rad(FLAGS.test_antenna_angle),
        FLAGS.max_iterations,
        FLAGS.tolerance,
    )

    calibrations: list[ProbeCalibration] = []
    for measurement in loader.load(
            frequencies,
            FLAGS.yaw_step,
            FLAGS.roll_step,
    ):
        max_degree = MeasurementFlags.max_degree(measurement)
        logging.info("Frequency: %.6f GHz, kA = %.2f, N = %d.",
                     measurement.frequency / 1e9, measurement.kA, max_degree)

        calibration = calibrator.calibrate(measurement, max_degree)
        probe_coefficients = calibration.probe_coefficients
        logging.info(
            "Relative residual = %.3e, boresight realized gain = %.2f dBi, "
            "radiated/available power = %.3f.",
            calibration.transmission_formula.relative_residual(
                measurement, calibration.test_coefficients),
            constants.power2db(
                probe_coefficients.realized_gain(np.array([0]),
                                                 np.array([0]))[0]),
            probe_coefficients.total_power(),
        )
        calibrations.append(calibration)

    SphericalWaveCoefficients.save(
        FLAGS.output,
        frequencies,
        [calibration.probe_coefficients for calibration in calibrations],
    )
    logging.info("Saved the probe coefficients to %s.", FLAGS.output)

    MeasurementFlags.create_plotter().plot(
        [calibration.test_coefficients for calibration in calibrations],
        frequencies,
        FLAGS.labels,
        "Probe Antenna",
    )


if __name__ == "__main__":
    MeasurementFlags.define_flags()
    flags.DEFINE_float(
        "test_antenna_angle", 0,
        "Polarization angle of the test antenna in degrees at zero roll from "
        "the +y-axis (up), right-handed around the +z-axis (toward the "
        "probe).")
    flags.DEFINE_integer("max_iterations", 50, "Maximum number of iterations.")
    flags.DEFINE_float("tolerance", 1e-8,
                       "Relative change in the probe coefficients to stop.")
    flags.DEFINE_string("output", None,
                        "Output CSV file for the probe coefficients.")
    flags.mark_flag_as_required("output")

    app.run(main)
