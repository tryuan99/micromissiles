"""Plots the reflectance of single-reflection paths."""

import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from absl import app, flags

from simulation.antenna.horn_antenna import HornAntenna
from simulation.antenna.patch_antenna import PatchAntenna
from utils import constants

FLAGS = flags.FLAGS

# Single-reflection path distances.
DISTANCES = np.arange(0.01, 11, 0.01)

# Radar cross sections in dBsm.
RADAR_CROSS_SECTIONS = np.arange(-20, 20, 10)


def plot_reflectance_for_single_reflection_path(range: float) -> None:
    """Plots the reflectance of single-reflection paths.

    A patch antenna is used as the transmitting antenna, and a horn antenna is
    used as the receiving antenna.

    Args:
        range: Direct line-of-sight distance in meters.
    """
    path_length = 2 * np.sqrt(DISTANCES**2 + range**2)
    alpha = np.arccos(range / (2 * path_length))

    # Define the antennas.
    tx_antenna = PatchAntenna(width=0.5, length=0.5)
    rx_antenna = HornAntenna(a=0.5, b=0.25, a1=5.5, b1=2.75, rho1=6, rho2=6)

    # Calculate the reflectance and plot it as a function of the distance.
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 8))
    for rcs_index, rcs in enumerate(RADAR_CROSS_SECTIONS):
        azimuth_reflectance = constants.power2db(
            tx_antenna.calculate_pattern(azimuth=alpha, elevation=0) *
            rx_antenna.calculate_pattern(azimuth=alpha, elevation=0) /
            (tx_antenna.calculate_pattern(azimuth=0, elevation=0) *
             rx_antenna.calculate_pattern(azimuth=0, elevation=0)) * range**2 /
            (4 * np.pi * path_length**4)) + rcs
        ax.plot(DISTANCES,
                azimuth_reflectance,
                color=f"C{rcs_index}",
                linestyle="-",
                label=fr"$\sigma = {rcs}$ dBsm (azimuth)")

        elevation_reflectance = constants.power2db(
            tx_antenna.calculate_pattern(azimuth=0, elevation=alpha) *
            rx_antenna.calculate_pattern(azimuth=0, elevation=alpha) /
            (tx_antenna.calculate_pattern(azimuth=0, elevation=0) *
             rx_antenna.calculate_pattern(azimuth=0, elevation=0)) * range**2 /
            (4 * np.pi * path_length**4)) + rcs
        ax.plot(DISTANCES,
                elevation_reflectance,
                color=f"C{rcs_index}",
                linestyle="--",
                label=fr"$\sigma = {rcs}$ dBsm (elevation)")
    ax.set_xlabel("Distance [m]")
    ax.set_ylabel("Reflectance [dB]")
    plt.legend()
    plt.show()


def main(argv):
    assert len(argv) == 1, argv

    plot_reflectance_for_single_reflection_path(FLAGS.range)


if __name__ == "__main__":
    flags.DEFINE_float("range",
                       0.8,
                       "Direct line-of-sight distance in meters.",
                       lower_bound=0.0)

    app.run(main)
