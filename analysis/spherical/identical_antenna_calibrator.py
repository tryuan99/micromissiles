"""Calibrates a probe by measuring an identical antenna.

Since both antennas are identical and reciprocal, the probe coefficients follow
from the solved test antenna coefficients. The transmission formula is solved
iteratively from a Huygens source as in Section 3.2.5 of J. E. Hansen (ed.),
"Spherical Near-Field Antenna Measurements", 1988, but with a single scan
instead of two.
"""

import numpy as np
from absl import logging

from analysis.spherical.probe_calibration import ProbeCalibration
from analysis.spherical.spherical_measurement import SphericalMeasurement
from analysis.spherical.spherical_wave_coefficients import \
    SphericalWaveCoefficients
from analysis.spherical.transmission_formula import TransmissionFormula


class IdenticalAntennaCalibrator:
    """Calibrates a probe by measuring an identical antenna.

    Each iteration solves for the test antenna with the current probe estimate,
    rotates the solution into the test antenna's own coordinate system, and
    updates the probe estimate. The probe coefficients are found up to a sign,
    and their scale is absolute if the VNA is calibrated at the antenna ports.

    Attributes:
        test_antenna_rotation: Rotation in radians around the boresight into
            the test antenna's own coordinate system.
        max_iterations: Maximum number of iterations.
        tolerance: Relative change in the probe coefficients to stop.
    """

    # An error with iteration gain lambda near 0 or -1 is scaled by
    # 1 - RELAXATION_FACTOR * (1 - lambda), i.e., by +/-1/3 for 2/3.
    RELAXATION_FACTOR = 2 / 3

    def __init__(
        self,
        test_antenna_angle: float,
        max_iterations: int,
        tolerance: float,
    ) -> None:
        """Initializes the calibrator.

        Args:
            test_antenna_angle: Polarization angle of the test antenna from
                vertical in radians at zero roll.
            max_iterations: Maximum number of iterations.
            tolerance: Relative change in the probe coefficients to stop.
        """
        self.test_antenna_rotation = np.pi / 2 + test_antenna_angle
        self.max_iterations = max_iterations
        self.tolerance = tolerance

    def calibrate(
        self,
        measurement: SphericalMeasurement,
        max_degree: int,
    ) -> ProbeCalibration:
        """Calibrates the probe at a single frequency.

        Args:
            measurement: Spherical near-field measurement of the test antenna.
            max_degree: Maximum degree N of the spherical wave expansion.

        Returns:
            The calibration of the probe at the measurement frequency.
        """
        probe_coefficients = SphericalWaveCoefficients.huygens_source(
            max_degree)
        for iteration in range(self.max_iterations):
            transmission_formula = TransmissionFormula(max_degree,
                                                       measurement.kA,
                                                       probe_coefficients)
            test_coefficients = transmission_formula.solve(measurement)
            updated_probe_coefficients = self._update(
                probe_coefficients,
                test_coefficients.rotate_around_z(self.test_antenna_rotation),
            )
            change = (np.linalg.norm(updated_probe_coefficients.values -
                                     probe_coefficients.values) /
                      np.linalg.norm(updated_probe_coefficients.values))
            probe_coefficients = updated_probe_coefficients
            logging.info("Iteration %d: relative change = %.3e.", iteration,
                         change)
            if change < self.tolerance:
                break

        # Solve with the final probe for consistent test antenna coefficients.
        transmission_formula = TransmissionFormula(
            max_degree,
            measurement.kA,
            probe_coefficients,
        )
        test_coefficients = transmission_formula.solve(measurement)
        return ProbeCalibration(
            probe_coefficients,
            test_coefficients,
            transmission_formula,
        )

    def _update(
        self,
        probe_coefficients: SphericalWaveCoefficients,
        solved_coefficients: SphericalWaveCoefficients,
    ) -> SphericalWaveCoefficients:
        """Updates the estimate of the probe coefficients.

        A current estimate c * T yields solved coefficients of about T / c, so c
        is estimated with least squares, and both estimates of T are combined
        with relaxation. Without it, an imbalance between mu = +1 and mu = -1
        would flip its sign every iteration without decaying.

        Args:
            probe_coefficients: Current estimate of the probe coefficients.
            solved_coefficients: Solved test antenna coefficients in the test
                antenna's own coordinate system.

        Returns:
            The updated estimate of the probe coefficients.
        """
        current = probe_coefficients.values
        solved = solved_coefficients.values
        scale = np.sqrt(np.vdot(solved, current) / np.vdot(solved, solved))
        updated = ((1 - self.RELAXATION_FACTOR) * current / scale +
                   self.RELAXATION_FACTOR * scale * solved)
        # Resolve the sign ambiguity by staying close to the current estimate.
        if np.real(np.vdot(current, updated)) < 0:
            updated *= -1
        return SphericalWaveCoefficients(updated)
