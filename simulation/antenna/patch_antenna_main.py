"""Plots the radiation pattern of a patch antenna."""

import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from absl import app, flags

from simulation.antenna.patch_antenna import PatchAntenna
from utils.visualization.color_maps import COLOR_MAPS

FLAGS = flags.FLAGS


def plot_radiation_pattern(width: float, length: float) -> None:
    """Plots the radiation pattern of a patch antenna.

    Args:
        width: Width in units of lambda.
        length: Length in units of lambda.
    """
    azimuth = np.linspace(-np.pi, np.pi, 720, endpoint=False)
    elevation = np.linspace(-np.pi / 2, np.pi / 2, 360, endpoint=False)
    theta, phi = np.meshgrid(azimuth, elevation)

    patch_antenna = PatchAntenna(width, length)
    pattern = patch_antenna.calculate_pattern(theta, phi)

    # Convert from spherical coordinates to Cartesian coordinates.
    r = 10 * np.log10(pattern + 1)
    x = r * np.cos(theta) * np.sin(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(phi)

    # Plot the radiation pattern.
    plt.style.use(["science"])
    fig, ax = plt.subplots(
        figsize=(12, 8),
        subplot_kw={"projection": "3d"},
    )
    surf = ax.plot_surface(
        x,
        y,
        z,
        cmap=COLOR_MAPS["parula"],
        antialiased=False,
    )
    ax.view_init(30, -45)
    plt.colorbar(surf)
    plt.show()


def main(argv):
    assert len(argv) == 1, argv

    plot_radiation_pattern(FLAGS.width, FLAGS.length)


if __name__ == "__main__":
    flags.DEFINE_float("width", 0.5, "Width in units of lambda.")
    flags.DEFINE_float("length", 0.5, "Length in units of lambda.")

    app.run(main)
