"""Plots the radiation pattern of a horn antenna."""

import matplotlib.colors
import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from absl import app, flags
from matplotlib import cm

from simulation.antenna.horn_antenna import HornAntenna
from utils.visualization.color_maps import COLOR_MAPS

FLAGS = flags.FLAGS


def plot_radiation_pattern_3d(a: float, b: float, a1: float, b1: float,
                              rho1: float, rho2: float) -> None:
    """Plots the 3D radiation pattern of a horn antenna.

    Args:
        a: Width in units of lambda before the flare.
        b: Height in uints of lambda before the flare.
        a1: Width in units of lambda after the flare.
        b1: Height in units of lambda after the flare.
        rho1: Depth of the pyramid in the y-z plane in units of lambda.
        rho2: Depth of the pyramid in the x-z plane in units of lambda.
    """
    azimuth = np.linspace(-np.pi, np.pi, 720, endpoint=False)
    elevation = np.linspace(-np.pi / 2, np.pi / 2, 360, endpoint=False)
    theta, phi = np.meshgrid(azimuth, elevation)

    horn_antenna = HornAntenna(a, b, a1, b1, rho1, rho2)
    pattern = horn_antenna.calculate_pattern(theta, phi)

    # Convert from spherical coordinates to Cartesian coordinates.
    r = 10 * np.log10(pattern + 1)
    x = -r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(phi)
    z = r * np.cos(theta) * np.cos(phi)

    # Generate the face colors.
    norm = matplotlib.colors.Normalize(vmin=np.min(r), vmax=np.max(r))
    m = cm.ScalarMappable(cmap=COLOR_MAPS["parula"], norm=norm)
    m.set_array([])

    # Plot the radiation pattern.
    plt.style.use("science")
    fig, ax = plt.subplots(
        figsize=(12, 8),
        subplot_kw={"projection": "3d"},
    )
    ax.plot_surface(
        x,
        y,
        z,
        facecolors=COLOR_MAPS["parula"](norm(r)),
        shade=False,
        antialiased=False,
    )
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.set_zlabel(r"$z$")
    ax.set_aspect("equal", adjustable="box")
    ax.view_init(30, -45)
    plt.colorbar(m, ax=ax)
    plt.show()


def plot_radiation_pattern_2d(a: float, b: float, a1: float, b1: float,
                              rho1: float, rho2: float) -> None:
    """Plots the 2D radiation pattern of a horn antenna along zero elevation and
    along zero azimuth.

    Args:
        a: Width in units of lambda before the flare.
        b: Height in uints of lambda before the flare.
        a1: Width in units of lambda after the flare.
        b1: Height in units of lambda after the flare.
        rho1: Depth of the pyramid in the y-z plane in units of lambda.
        rho2: Depth of the pyramid in the x-z plane in units of lambda.
    """
    horn_antenna = HornAntenna(a, b, a1, b1, rho1, rho2)

    # Plot the radiation pattern along zero elevation.
    azimuth = np.linspace(-np.pi, np.pi, 720, endpoint=False)
    pattern = horn_antenna.calculate_pattern(azimuth=azimuth, elevation=0)
    plt.style.use("science")
    fig, ax = plt.subplots(
        figsize=(12, 8),
        subplot_kw={"projection": "polar"},
    )
    ax.plot(azimuth, 10 * np.log10(pattern + 1))
    ax.set_xlabel(r"Azimuth $\theta$")
    plt.show()

    # Plot the radiation pattern along zero azimuth.
    elevation = np.linspace(-np.pi / 2, np.pi / 2, 360, endpoint=False)
    pattern = horn_antenna.calculate_pattern(azimuth=0, elevation=elevation)
    plt.style.use("science")
    fig, ax = plt.subplots(
        figsize=(12, 8),
        subplot_kw={"projection": "polar"},
    )
    ax.plot(elevation, 10 * np.log10(pattern + 1))
    ax.set_xlabel(r"Elevation $\phi$")
    plt.show()


def main(argv):
    assert len(argv) == 1, argv

    plot_radiation_pattern_3d(FLAGS.a, FLAGS.b, FLAGS.a1, FLAGS.b1, FLAGS.rho1,
                              FLAGS.rho2)
    plot_radiation_pattern_2d(FLAGS.a, FLAGS.b, FLAGS.a1, FLAGS.b1, FLAGS.rho1,
                              FLAGS.rho2)


if __name__ == "__main__":
    flags.DEFINE_float("a", 0.5, "Width in units of lambda before the flare.")
    flags.DEFINE_float("b", 0.25, "Height in units of lambda before the flare.")
    flags.DEFINE_float("a1", 5.5, "Width in units of lambda after the flare.")
    flags.DEFINE_float("b1", 2.75, "Height in units of lambda after the flare.")
    flags.DEFINE_float(
        "rho1", 6, "Depth of the pyramid in the y-z plane in units of lambda.")
    flags.DEFINE_float(
        "rho2", 6, "Depth of the pyramid in the x-z plane in units of lambda.")

    app.run(main)
