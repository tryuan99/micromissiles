"""Probe response constants of a mu = +/-1 probe.

The notation and equation numbers follow J. E. Hansen (ed.), "Spherical
Near-Field Antenna Measurements", IET Electromagnetic Waves Series 26, 1988.
"""

import numpy as np

from analysis.spherical.spherical_wave_coefficients import \
    SphericalWaveCoefficients
from analysis.spherical.translation_coefficients import TranslationCoefficients


class ProbeResponseConstants:
    """Probe response constants P_{s mu n}(kA) for mu = +/-1.

    See eqn (3.26) or eqn (4.39). Only the probe receiving coefficients with
    mu = +/-1 contribute.
    """

    # Azimuthal probe indices mu.
    PROBE_MU = np.array([-1, 1])

    @staticmethod
    def evaluate(probe_coefficients: SphericalWaveCoefficients, kA: float,
                 max_degree: int) -> np.ndarray:
        """Evaluates the probe response constants.

        Args:
            probe_coefficients: Probe transmitting coefficients in the probe's
                own coordinate system.
            kA: Wavenumber times the measurement distance.
            max_degree: Maximum degree N of the test antenna.

        Returns:
            An array of shape (2, 2, N + 1), where entry [s - 1, mu index, n]
            contains P_{s mu n}(kA) and mu index 0 and 1 correspond to mu = -1
            and mu = +1, respectively.
        """
        receiving_coefficients = ProbeResponseConstants._receiving_coefficients(
            probe_coefficients)
        probe_max_degree = receiving_coefficients.max_degree
        translation = TranslationCoefficients.evaluate(kA, max_degree,
                                                       probe_max_degree)
        mu_indices = ProbeResponseConstants.PROBE_MU + probe_max_degree
        # Receiving coefficients R^p_{sigma mu nu} with shape (sigma, mu, nu).
        receiving = receiving_coefficients.values[:, :, mu_indices].transpose(
            0, 2, 1)
        return 0.5 * np.einsum("sjunv,juv->sun", translation, receiving)

    @staticmethod
    def _receiving_coefficients(
        probe_coefficients: SphericalWaveCoefficients,
    ) -> SphericalWaveCoefficients:
        """Computes the probe receiving coefficients R^p_{sigma mu nu}.

        The probe transmitting coefficients are defined in the probe's own
        coordinate system with the boresight along +z. In the transmission
        formula, the primed probe coordinate system has its z'-axis pointing
        away from the test antenna, so the probe is rotated by pi about its
        y-axis before applying reciprocity.

        Args:
            probe_coefficients: Probe transmitting coefficients in the probe's
                own coordinate system.

        Returns:
            The probe receiving coefficients in the primed probe coordinate
            system.
        """
        return probe_coefficients.rotate_about_y(np.pi).receiving_coefficients()
