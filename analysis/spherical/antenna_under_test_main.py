"""Solves for the spherical wave coefficients of the antenna under test and
plots the extrapolated far-field radiation pattern.

The transmission formula is solved with probe correction as in Section 4.3 of
J. E. Hansen (ed.), "Spherical Near-Field Antenna Measurements", 1988, using
the probe horn coefficients from probe_calibration_main.
"""

import numpy as np
from absl import app, flags, logging

import utils.visualization.mpl_config
from analysis.antenna.marlin.common import RadiationPatternSlice
from analysis.spherical.radiation_pattern_plotter import RadiationPatternPlotter
from analysis.spherical.spherical_measurement import (
    CsvSphericalMeasurementLoader, PositionerGeometry,
    SphericalMeasurementLoader)
from analysis.spherical.spherical_wave_coefficients import \
    SphericalWaveCoefficients
from analysis.spherical.transmission_formula import TransmissionFormula

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

    probe_frequencies, probe_coefficients, probe_metadata = (
        SphericalWaveCoefficients.load(FLAGS.probe_coefficients))
    if not np.isclose(probe_metadata["distance"], FLAGS.distance):
        logging.warning(
            "The probe was calibrated at a distance of %.4f m, but the "
            "measurement distance is %.4f m.", probe_metadata["distance"],
            FLAGS.distance)

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

    # Far-field grid for finding the peak realized gain.
    grid_theta, grid_phi = np.meshgrid(
        np.linspace(0, np.pi, NUM_PEAK_SEARCH_THETAS),
        np.linspace(0, 2 * np.pi, NUM_PEAK_SEARCH_PHIS, endpoint=False),
    )
    grid_theta = grid_theta.ravel()
    grid_phi = grid_phi.ravel()

    coefficients_per_frequency = []
    for measurement in loader.load(frequencies):
        probe_indices = np.flatnonzero(
            np.isclose(probe_frequencies, measurement.frequency))
        if len(probe_indices) == 0:
            raise ValueError(f"The probe was not calibrated at "
                             f"{measurement.frequency / 1e9} GHz.")

        max_degree = (FLAGS.max_degree if FLAGS.max_degree is not None else
                      SphericalWaveCoefficients.max_degree_for_radius(
                          measurement.wavenumber, FLAGS.min_sphere_radius))
        logging.info("Frequency: %.6f GHz, kA = %.2f, N = %d.",
                     measurement.frequency / 1e9, measurement.kA, max_degree)

        transmission_formula = TransmissionFormula(
            probe_coefficients[probe_indices[0]],
            measurement.kA,
            max_degree,
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
            10 * np.log10(gain[peak_index]),
            np.rad2deg(grid_theta[peak_index]),
            np.rad2deg(grid_phi[peak_index]),
            10 * np.log10(gain[peak_index] / efficiency),
            efficiency,
        )
        coefficients_per_frequency.append(coefficients)

    if FLAGS.output:
        SphericalWaveCoefficients.save(FLAGS.output, frequencies,
                                       coefficients_per_frequency)
        logging.info("Saved the antenna coefficients to %s.", FLAGS.output)

    plotter = RadiationPatternPlotter(
        RadiationPatternSlice(FLAGS.slice),
        FLAGS.polarization == "vertical",
    )
    plotter.plot(coefficients_per_frequency, FLAGS.labels, "Antenna under test")


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
    flags.DEFINE_string("probe_coefficients", None,
                        "Probe coefficients NPZ file from the calibration.")
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
        "Radius in meters of the minimum sphere enclosing the antenna under "
        "test centered at the intersection of the yaw and the roll axes.",
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
    flags.DEFINE_string(
        "output",
        None,
        "Optional output NPZ file for the antenna coefficients.",
    )
    flags.DEFINE_enum("slice", RadiationPatternSlice.AZIMUTH.value, [
        radiation_pattern_slice.value
        for radiation_pattern_slice in RadiationPatternSlice
    ], "Radiation pattern slice.")
    flags.DEFINE_enum("polarization", "vertical", ["vertical", "horizontal"],
                      "Co-polarization of the antenna under test.")
    flags.mark_flags_as_required([
        "probe_coefficients",
        "yaw_step",
        "roll_step",
        "distance",
        "frequencies",
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
