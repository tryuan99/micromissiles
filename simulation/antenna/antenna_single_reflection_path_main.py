"""Plots the reflectance of single-reflection paths."""

import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from absl import app, flags

from simulation.antenna.antenna import Antenna
from simulation.antenna.horn_antenna import HornAntenna
from simulation.antenna.patch_antenna import PatchAntenna
from utils import constants

FLAGS = flags.FLAGS

# Single-reflection path distances in meters.
DISTANCES = np.arange(0.01, 11, 0.01)

# Radar cross sections in dBsm.
RADAR_CROSS_SECTIONS = np.arange(-20, 20, 10)

# Azimuth angles in radians.
AZIMUTHS = np.arange(0, 90, 15) * np.pi / 180

# Elevation angles in radians.
ELEVATIONS = np.arange(0, 90, 15) * np.pi / 180


def plot_reflectance_for_single_reflection_path_at_boresight(
        range: float, tx_antenna: Antenna, rx_antenna: Antenna) -> None:
    """Plots the reflectance of single-reflection paths at boresight.

    Args:
        range: Direct line-of-sight distance in meters.
        tx_antenna: TX antenna.
        rx_antenna: RX antenna.
    """
    r = np.sqrt(DISTANCES**2 + (range / 2)**2)
    alpha = np.arccos(range / (2 * r))

    # Calculate the reflectance for each radar cross section and plot it as a
    # function of the distance.
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 8))
    for rcs_index, rcs in enumerate(RADAR_CROSS_SECTIONS):
        azimuth_reflectance = constants.power2db(
            tx_antenna.calculate_pattern(azimuth=-alpha, elevation=0) *
            rx_antenna.calculate_pattern(azimuth=alpha, elevation=0) /
            (tx_antenna.calculate_pattern(azimuth=0, elevation=0) *
             rx_antenna.calculate_pattern(azimuth=0, elevation=0)) * range**2 /
            (4 * np.pi * r**4)) + rcs
        ax.plot(DISTANCES,
                azimuth_reflectance,
                color=f"C{rcs_index}",
                linestyle="--",
                label=rf"$\sigma = {rcs}$ dBsm (azimuth)")

        elevation_reflectance = constants.power2db(
            tx_antenna.calculate_pattern(azimuth=0, elevation=alpha) *
            rx_antenna.calculate_pattern(azimuth=0, elevation=alpha) /
            (tx_antenna.calculate_pattern(azimuth=0, elevation=0) *
             rx_antenna.calculate_pattern(azimuth=0, elevation=0)) * range**2 /
            (4 * np.pi * r**4)) + rcs
        ax.plot(DISTANCES,
                elevation_reflectance,
                color=f"C{rcs_index}",
                linestyle=":",
                label=rf"$\sigma = {rcs}$ dBsm (elevation)")
    ax.axhline(-40, color="black", linestyle="-", label="Reflectance threshold")
    ax.set_xlabel("Distance [m]")
    ax.set_ylabel("Reflectance [dB]")
    plt.legend()
    plt.show()


def plot_reflectance_for_single_reflection_path_over_azimuth(
        range: float, rcs: float, tx_antenna: Antenna,
        rx_antenna: Antenna) -> None:
    """Plots the reflectance of single-reflection paths over azimuth.

    Args:
        range: Direct line-of-sight distance in meters.
        rcs: Radar cross section in dBsm.
        tx_antenna: TX antenna.
        rx_antenna: RX antenna.
    """
    r = np.sqrt(DISTANCES**2 + (range / 2)**2)
    alpha = np.arccos(range / (2 * r))

    # Calculate the reflectance for each azimuth and plot it as a function of
    # the distance.
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 8))
    for azimuth in AZIMUTHS:
        azimuth_reflectance = constants.power2db(
            tx_antenna.calculate_pattern(azimuth=azimuth - alpha, elevation=0) *
            rx_antenna.calculate_pattern(azimuth=alpha, elevation=0) /
            (tx_antenna.calculate_pattern(azimuth=azimuth, elevation=0) *
             rx_antenna.calculate_pattern(azimuth=0, elevation=0)) * range**2 /
            (4 * np.pi * r**4)) + rcs
        ax.plot(DISTANCES,
                azimuth_reflectance,
                linestyle="--",
                label=rf"$\theta = {azimuth * 180 / np.pi:.2f}^\circ$")
    ax.axhline(-40, color="black", linestyle="-", label="Reflectance threshold")
    ax.set_xlabel("Distance [m]")
    ax.set_ylabel("Reflectance [dB]")
    plt.legend()
    plt.show()


def plot_reflectance_for_single_reflection_path_over_elevation(
        range: float, rcs: float, tx_antenna: Antenna,
        rx_antenna: Antenna) -> None:
    """Plots the reflectance of single-reflection paths over elevation.

    Args:
        range: Direct line-of-sight distance in meters.
        rcs: Radar cross section in dBsm.
        tx_antenna: TX antenna.
        rx_antenna: RX antenna.
    """
    r = np.sqrt(DISTANCES**2 + (range / 2)**2)
    alpha = np.arccos(range / (2 * r))

    # Calculate the reflectance for each elevation and plot it as a function of
    # the distance.
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 8))
    for elevation in ELEVATIONS:
        elevation_reflectance = constants.power2db(
            tx_antenna.calculate_pattern(azimuth=0, elevation=elevation - alpha)
            * rx_antenna.calculate_pattern(azimuth=0, elevation=-alpha) /
            (tx_antenna.calculate_pattern(azimuth=0, elevation=elevation) *
             rx_antenna.calculate_pattern(azimuth=0, elevation=0)) * range**2 /
            (4 * np.pi * r**4)) + rcs
        ax.plot(DISTANCES,
                elevation_reflectance,
                linestyle="--",
                label=rf"$\phi = {elevation * 180 / np.pi:.2f}^\circ$")
    ax.axhline(-40, color="black", linestyle="-", label="Reflectance threshold")
    ax.set_xlabel("Distance [m]")
    ax.set_ylabel("Reflectance [dB]")
    plt.legend()
    plt.show()


def plot_reflectance_for_single_reflection_path_over_azimuth_and_elevation(
        range: float, rcs: float, tx_antenna: Antenna,
        rx_antenna: Antenna) -> None:
    """Plots the reflectance of single-reflection paths over azimuth and
    elevation.

    Args:
        range: Direct line-of-sight distance in meters.
        rcs: Radar cross section in dBsm.
        tx_antenna: TX antenna.
        rx_antenna: RX antenna.
    """
    r = np.sqrt(DISTANCES**2 + (range / 2)**2)
    alpha = np.arccos(range / (2 * r))

    # Calculate the reflectance for each azimuth and elevation and plot it as a
    # function of the distance.
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 8))
    for azimuth in AZIMUTHS[-2:]:
        for elevation in ELEVATIONS[-2:]:
            reflectance = constants.power2db(
                tx_antenna.calculate_pattern(azimuth=azimuth - alpha,
                                             elevation=elevation - alpha) *
                rx_antenna.calculate_pattern(azimuth=alpha, elevation=-alpha) /
                (tx_antenna.calculate_pattern(azimuth=azimuth,
                                              elevation=elevation) *
                 rx_antenna.calculate_pattern(azimuth=0, elevation=0)) *
                range**2 / (4 * np.pi * r**4)) + rcs
            ax.plot(DISTANCES,
                    reflectance,
                    linestyle="--",
                    label=(rf"$\theta = {azimuth * 180 / np.pi:.2f}^\circ$, "
                           rf"$\phi = {elevation * 180 / np.pi:.2f}^\circ$"))
    ax.axhline(-40, color="black", linestyle="-", label="Reflectance threshold")
    ax.set_xlabel("Distance [m]")
    ax.set_ylabel("Reflectance [dB]")
    plt.legend()
    plt.show()


def main(argv):
    assert len(argv) == 1, argv

    # Define the antennas.
    tx_antenna = PatchAntenna(width=0.5, length=0.5)
    # Horn antenna dimensions based on
    # https://www.pasternack.com/images/ProductPDF/PE9881-24.pdf at 60 GHz.
    rx_antenna = HornAntenna(a=0.772,
                             b=0.376,
                             a1=7.5,
                             b1=5.78,
                             rho1=14.12,
                             rho2=14.12)

    plot_reflectance_for_single_reflection_path_at_boresight(
        FLAGS.range, tx_antenna, rx_antenna)
    plot_reflectance_for_single_reflection_path_over_azimuth(
        FLAGS.range, FLAGS.rcs, tx_antenna, rx_antenna)
    plot_reflectance_for_single_reflection_path_over_elevation(
        FLAGS.range, FLAGS.rcs, tx_antenna, rx_antenna)
    plot_reflectance_for_single_reflection_path_over_azimuth_and_elevation(
        FLAGS.range, FLAGS.rcs, tx_antenna, rx_antenna)


if __name__ == "__main__":
    flags.DEFINE_float("range",
                       0.8,
                       "Direct line-of-sight distance in meters.",
                       lower_bound=0.0)
    flags.DEFINE_float("rcs", 10, "Radar cross section in dBsm.")

    app.run(main)
