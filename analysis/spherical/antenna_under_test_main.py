"""Solves for the spherical wave coefficients of the antenna under test and
plots the extrapolated far-field radiation pattern.

The transmission formula is solved with probe correction as in Section 4.3 of
J. E. Hansen (ed.), "Spherical Near-Field Antenna Measurements", 1988, using the
probe coefficients from probe_calibration_main.
"""

import numpy as np
from absl import app, flags, logging

import utils.visualization.mpl_config
from analysis.spherical.measurement_flags import MeasurementFlags
from analysis.spherical.spherical_wave_coefficients import \
    SphericalWaveCoefficients
from analysis.spherical.transmission_formula import TransmissionFormula
from utils import constants

FLAGS = flags.FLAGS

# Number of theta and phi samples for finding the peak realized gain.
NUM_PEAK_SEARCH_THETAS = 181
NUM_PEAK_SEARCH_PHIS = 360


def main(argv):
    """Solves for the antenna under test and plots its radiation pattern.

    Args:
        argv: Command-line arguments.
    """
    assert len(argv) == 1

    probe_frequencies, probe_coefficients = SphericalWaveCoefficients.load(
        FLAGS.probe_coefficients)
    frequencies = np.array(FLAGS.frequencies)
    loader = MeasurementFlags.create_loader()

    # Far-field grid for finding the peak realized gain.
    grid_theta, grid_phi = np.meshgrid(
        np.linspace(0, np.pi, NUM_PEAK_SEARCH_THETAS),
        np.linspace(0, 2 * np.pi, NUM_PEAK_SEARCH_PHIS, endpoint=False),
    )
    grid_theta = grid_theta.ravel()
    grid_phi = grid_phi.ravel()

    coefficients_per_frequency = []
    for measurement in loader.load(frequencies, FLAGS.yaw_step,
                                   FLAGS.roll_step):
        probe_indices = np.flatnonzero(
            np.isclose(probe_frequencies, measurement.frequency))
        if len(probe_indices) == 0:
            raise ValueError(f"The probe was not calibrated at "
                             f"{measurement.frequency / 1e9} GHz.")

        max_degree = MeasurementFlags.max_degree(measurement)
        logging.info("Frequency: %.6f GHz, kA = %.2f, N = %d.",
                     measurement.frequency / 1e9, measurement.kA, max_degree)

        transmission_formula = TransmissionFormula(
            max_degree,
            measurement.kA,
            probe_coefficients[probe_indices[0]],
        )
        coefficients = transmission_formula.solve(measurement)

        gain = coefficients.realized_gain(grid_theta, grid_phi)
        peak_index = np.argmax(gain)
        efficiency = coefficients.total_power()
        logging.info(
            "Relative residual = %.3e, peak realized gain = %.2f dBi at "
            "(theta, phi) = (%.1f, %.1f) deg, peak directivity = %.2f dBi, "
            "radiated/available power = %.3f.",
            transmission_formula.relative_residual(measurement, coefficients),
            constants.power2db(gain[peak_index]),
            constants.rad2deg(grid_theta[peak_index]),
            constants.rad2deg(grid_phi[peak_index]),
            constants.power2db(gain[peak_index] / efficiency),
            efficiency,
        )
        coefficients_per_frequency.append(coefficients)

    if FLAGS.output:
        SphericalWaveCoefficients.save(FLAGS.output, frequencies,
                                       coefficients_per_frequency)
        logging.info("Saved the antenna coefficients to %s.", FLAGS.output)

    MeasurementFlags.create_plotter().plot(
        coefficients_per_frequency,
        frequencies,
        FLAGS.labels,
        "Antenna Under Test",
    )


if __name__ == "__main__":
    MeasurementFlags.define_flags()
    flags.DEFINE_string("probe_coefficients", None,
                        "Probe coefficients CSV file from the calibration.")
    flags.DEFINE_string(
        "output",
        None,
        "Optional output CSV file for the antenna coefficients.",
    )
    flags.mark_flag_as_required("probe_coefficients")

    app.run(main)
