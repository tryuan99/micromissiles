"""Calibration of the probe at a single frequency."""

from dataclasses import dataclass

from analysis.spherical.spherical_wave_coefficients import \
    SphericalWaveCoefficients
from analysis.spherical.transmission_formula import TransmissionFormula


@dataclass
class ProbeCalibration:
    """Calibration of the probe at a single frequency.

    Attributes:
        probe_coefficients: Probe coefficients in the probe's own coordinate
            system.
        test_coefficients: Test antenna coefficients in the test antenna
            coordinate system.
        transmission_formula: Transmission formula with the final probe.
    """
    probe_coefficients: SphericalWaveCoefficients
    test_coefficients: SphericalWaveCoefficients
    transmission_formula: TransmissionFormula
