"""Plots the far-field radiation pattern from spherical wave coefficients."""

import matplotlib.pyplot as plt
import numpy as np

from analysis.antenna.marlin.common import RadiationPatternSlice
from analysis.spherical.spherical_wave_coefficients import \
    SphericalWaveCoefficients
from utils import constants


class RadiationPatternPlotter:
    """Plots the co- and cross-polarized realized gain of a pattern slice.

    The azimuth slice lies in the horizontal xz-plane with positive azimuth
    toward -x, i.e., to the right when looking from behind the antenna along
    its boresight. The elevation slice lies in the vertical yz-plane with
    positive elevation toward +y (up). The co- and cross-polarization follow
    Ludwig's third definition.

    Attributes:
        slice: Radiation pattern slice.
        vertical: If true, the co-polarization is vertical (+y). Otherwise, the
            co-polarization is horizontal (+x).
    """

    # Number of plotted angles from -180 to 180 degrees.
    NUM_ANGLES = 721

    # Plotted dynamic range in dB.
    DYNAMIC_RANGE = 50

    def __init__(self, slice: RadiationPatternSlice, vertical: bool) -> None:
        """Initializes the plotter.

        Args:
            slice: Radiation pattern slice.
            vertical: If true, the co-polarization is vertical.
        """
        self.slice = slice
        self.vertical = vertical

    def plot(
        self,
        coefficients: list[SphericalWaveCoefficients],
        labels: list[str] | None,
        title: str,
    ) -> None:
        """Plots the realized gain in Cartesian and polar coordinates.

        Args:
            coefficients: Transmitting coefficients for each frequency.
            labels: Labels for each frequency.
            title: Plot title.
        """
        positions = np.linspace(-180, 180, self.NUM_ANGLES)
        theta, phi = self._slice_angles(np.deg2rad(positions))
        co_gains = []
        cross_gains = []
        for frequency_coefficients in coefficients:
            co, cross = self._ludwig3_components(frequency_coefficients, theta,
                                                 phi)
            co_gains.append(constants.power2db(np.abs(co)**2))
            cross_gains.append(constants.power2db(np.abs(cross)**2))
        peak_gain = np.max(co_gains)

        fig, ax = plt.subplots(figsize=(6, 6))
        self._plot_gains(ax, positions, co_gains, cross_gains, labels)
        ax.set_ylim(peak_gain - self.DYNAMIC_RANGE, peak_gain + 5)
        ax.set_xlabel(f"{self.slice.capitalize()} [deg]")
        ax.set_ylabel("Realized Gain [dBi]")
        ax.set_title(title)
        ax.legend()
        plt.show()

        fig, ax = plt.subplots(
            figsize=(6, 6),
            subplot_kw={"projection": "polar"},
        )
        if self.slice != RadiationPatternSlice.ELEVATION:
            ax.set_theta_zero_location("N")
            ax.set_theta_direction(-1)
        self._plot_gains(ax, np.deg2rad(positions), co_gains, cross_gains,
                         labels)
        ax.set_rlim(peak_gain - self.DYNAMIC_RANGE, peak_gain + 5)
        ax.set_thetamin(-180)
        ax.set_thetamax(180)
        ax.set_title(title)
        ax.legend()
        plt.show()

    @staticmethod
    def _plot_gains(
        ax: plt.Axes,
        positions: np.ndarray,
        co_gains: list[np.ndarray],
        cross_gains: list[np.ndarray],
        labels: list[str] | None,
    ) -> None:
        """Plots the co- and cross-polarized gains on the given axes.

        Args:
            ax: Axes to plot on.
            positions: Angles of the slice.
            co_gains: Co-polarized realized gain in dBi for each frequency.
            cross_gains: Cross-polarized realized gain in dBi for each
                frequency.
            labels: Labels for each frequency.
        """
        for frequency_index, (co_gain, cross_gain) in enumerate(
                zip(co_gains, cross_gains)):
            label = (labels[frequency_index]
                     if labels else f"{frequency_index}")
            ax.plot(
                positions,
                co_gain,
                color=f"C{frequency_index}",
                label=f"{label} (co-pol)",
            )
            ax.plot(
                positions,
                cross_gain,
                color=f"C{frequency_index}",
                linestyle="--",
                label=f"{label} (cross-pol)",
            )

    def _slice_angles(self,
                      angles: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Converts the angles of the slice into theta and phi.

        Args:
            angles: Angles in radians from -pi to pi.

        Returns:
            A 2-tuple consisting of theta and phi in radians.
        """
        positive_phi = (np.pi if self.slice == RadiationPatternSlice.AZIMUTH
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
        """Decomposes the far field into the co- and cross-polarization.

        Args:
            coefficients: Transmitting coefficients.
            theta: Theta in radians.
            phi: Phi in radians.

        Returns:
            A 2-tuple consisting of the co-polarized and the cross-polarized
            far-field components.
        """
        k_theta, k_phi = coefficients.far_field(theta, phi)
        x_component = k_theta * np.cos(phi) - k_phi * np.sin(phi)
        y_component = k_theta * np.sin(phi) + k_phi * np.cos(phi)
        if self.vertical:
            return y_component, x_component
        return x_component, y_component
