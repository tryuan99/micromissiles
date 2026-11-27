"""Plots the far-field radiation pattern from spherical wave coefficients."""

from enum import StrEnum

import matplotlib.pyplot as plt
import numpy as np

from analysis.spherical.spherical_wave_coefficients import \
    SphericalWaveCoefficients
from utils import constants


class Polarization(StrEnum):
    """Polarization enumeration."""
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"


class RadiationPatternSlice(StrEnum):
    """Radiation pattern slice enumeration."""
    AZIMUTH = "azimuth"
    ELEVATION = "elevation"


class RadiationPatternPlotter:
    """Plots the copolarized and cross-polarized realized gain of both slices.

    The azimuth slice lies in the horizontal xz-plane with positive azimuth
    toward the -x-axis, i.e., to the right when looking from behind the antenna
    along its boresight. The elevation slice lies in the vertical yz-plane with
    positive elevation toward the +y-axis (up). The copolarization and the
    cross-polarization follow Ludwig's third definition.

    Attributes:
        polarization: Polarization of the test antenna, i.e., the
            copolarization along the +y-axis if vertical and along the +x-axis
            if horizontal.
    """

    # Number of plotted angles from -180 to 180 degrees.
    NUM_ANGLES = 721

    # Plotted dynamic range in dB.
    DYNAMIC_RANGE = 50

    def __init__(self, polarization: Polarization) -> None:
        """Initializes the plotter.

        Args:
            polarization: Polarization of the test antenna.
        """
        self.polarization = polarization

    def plot(
        self,
        coefficients: list[SphericalWaveCoefficients],
        frequencies: np.ndarray,
        labels: list[str] | None,
        title: str,
    ) -> None:
        """Plots the realized gain of both slices in Cartesian and polar axes.

        Args:
            coefficients: Transmitting coefficients for each frequency.
            frequencies: Frequencies in Hz.
            labels: Labels for each frequency, or None to label each frequency
                in GHz.
            title: Plot title.

        Raises:
            ValueError: If there is not one label for each frequency.
        """
        if labels is None:
            labels = [f"{frequency / 1e9:g} GHz" for frequency in frequencies]
        if len(labels) != len(coefficients):
            raise ValueError("One label is required for each frequency.")
        positions = np.linspace(-180, 180, self.NUM_ANGLES)
        gains = {
            pattern_slice:
                self._gains(
                    coefficients,
                    constants.deg2rad(positions),
                    pattern_slice,
                ) for pattern_slice in RadiationPatternSlice
        }
        peak_gain = max(
            np.max(copolarized_gains)
            for copolarized_gains, _ in gains.values())

        fig, axes = plt.subplots(1, 2, figsize=(12, 6))
        for ax, pattern_slice in zip(axes, RadiationPatternSlice):
            copolarized_gains, cross_polarized_gains = gains[pattern_slice]
            self._plot_gains(ax, positions, copolarized_gains,
                             cross_polarized_gains, labels)
            ax.set_xlabel(f"{pattern_slice.capitalize()} [deg]")
            ax.set_ylabel("Realized Gain [dBi]")
            ax.set_title(pattern_slice.capitalize())
            ax.legend()
        fig.suptitle(title)

        fig, axes = plt.subplots(
            1,
            2,
            figsize=(12, 6),
            subplot_kw={"projection": "polar"},
        )
        for ax, pattern_slice in zip(axes, RadiationPatternSlice):
            copolarized_gains, cross_polarized_gains = gains[pattern_slice]
            if pattern_slice == RadiationPatternSlice.AZIMUTH:
                ax.set_theta_zero_location("N")
                ax.set_theta_direction(-1)
            self._plot_gains(ax, constants.deg2rad(positions),
                             copolarized_gains, cross_polarized_gains, labels)
            ax.set_rlim(peak_gain - self.DYNAMIC_RANGE, peak_gain + 5)
            ax.set_thetamin(-180)
            ax.set_thetamax(180)
            ax.set_title(f"{pattern_slice.capitalize()} Realized Gain [dBi]")
            ax.legend()
        fig.suptitle(title)
        plt.show()

    def _gains(
        self,
        coefficients: list[SphericalWaveCoefficients],
        angles: np.ndarray,
        pattern_slice: RadiationPatternSlice,
    ) -> tuple[list[np.ndarray], list[np.ndarray]]:
        """Computes the copolarized and cross-polarized gains of a slice.

        Args:
            coefficients: Transmitting coefficients for each frequency.
            angles: Angles of the slice in radians from -pi to pi.
            pattern_slice: Radiation pattern slice.

        Returns:
            A 2-tuple consisting of the copolarized and the cross-polarized
            realized gain in dBi for each frequency.
        """
        theta, phi = self._slice_angles(angles, pattern_slice)
        copolarized_gains = []
        cross_polarized_gains = []
        for frequency_coefficients in coefficients:
            copolarized, cross_polarized = self._ludwig3_components(
                frequency_coefficients, theta, phi)
            copolarized_gains.append(constants.power2db(np.abs(copolarized)**2))
            cross_polarized_gains.append(
                constants.power2db(np.abs(cross_polarized)**2))
        return copolarized_gains, cross_polarized_gains

    @staticmethod
    def _plot_gains(
        ax: plt.Axes,
        positions: np.ndarray,
        copolarized_gains: list[np.ndarray],
        cross_polarized_gains: list[np.ndarray],
        labels: list[str],
    ) -> None:
        """Plots the copolarized and cross-polarized gains on the given axes.

        Args:
            ax: Axes to plot on.
            positions: Angles of the slice.
            copolarized_gains: Copolarized realized gain in dBi for each
                frequency.
            cross_polarized_gains: Cross-polarized realized gain in dBi for each
                frequency.
            labels: Labels for each frequency.
        """
        for frequency_index in range(len(copolarized_gains)):
            color = f"C{frequency_index}"
            ax.plot(
                positions,
                copolarized_gains[frequency_index],
                color=color,
                label=f"{labels[frequency_index]} (copolarized)",
            )
            ax.plot(
                positions,
                cross_polarized_gains[frequency_index],
                color=color,
                linestyle="--",
                label=f"{labels[frequency_index]} (cross-polarized)",
            )

    @staticmethod
    def _slice_angles(
        angles: np.ndarray,
        pattern_slice: RadiationPatternSlice,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Converts the angles of the slice into theta and phi.

        Args:
            angles: Angles in radians from -pi to pi.
            pattern_slice: Radiation pattern slice.

        Returns:
            A 2-tuple consisting of theta and phi in radians.
        """
        positive_phi = (np.pi if pattern_slice == RadiationPatternSlice.AZIMUTH
                        else np.pi / 2)
        theta = np.abs(angles)
        phi = np.where(angles >= 0, positive_phi, positive_phi + np.pi)
        return theta, phi

    def _ludwig3_components(
        self,
        coefficients: SphericalWaveCoefficients,
        theta: np.ndarray,
        phi: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Decomposes the far field into copolarized and cross-polarized parts.

        Args:
            coefficients: Transmitting coefficients.
            theta: Theta in radians.
            phi: Phi in radians.

        Returns:
            A 2-tuple consisting of the copolarized and the cross-polarized
            far-field components.
        """
        k_theta, k_phi = coefficients.far_field(theta, phi)
        x_component = k_theta * np.cos(phi) - k_phi * np.sin(phi)
        y_component = k_theta * np.sin(phi) + k_phi * np.cos(phi)
        if self.polarization == Polarization.VERTICAL:
            return y_component, x_component
        return x_component, y_component
