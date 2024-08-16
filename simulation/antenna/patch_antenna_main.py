"""Plots the radiation pattern of a patch antenna."""

import matplotlib.colors
import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from absl import app, flags
from matplotlib import cm

from simulation.antenna.patch_antenna import PatchAntenna
from utils import constants
from utils.visualization.color_maps import COLOR_MAPS

FLAGS = flags.FLAGS


def plot_radiation_pattern_3d(width: float, length: float) -> None:
    """Plots the 3D radiation pattern of a patch antenna.

    Args:
        width: Width in units of lambda.
        length: Length in units of lambda.
    """
    azimuth = np.linspace(-np.pi / 2, np.pi / 2, 360, endpoint=False)
    elevation = np.linspace(-np.pi / 2, np.pi / 2, 360, endpoint=False)
    theta, phi = np.meshgrid(azimuth, elevation, indexing="ij")

    patch_antenna = PatchAntenna(width, length)
    pattern = patch_antenna.calculate_pattern(theta, phi)

    # Convert from spherical coordinates to Cartesian coordinates.
    r = constants.power2db(pattern + 1)
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


def plot_radiation_pattern_2d(width: float, length: float) -> None:
    """Plots the 2D radiation pattern of a patch antenna along zero elevation
    and along zero azimuth.

    Args:
        width: Width in units of lambda.
        length: Length in units of lambda.
    """
    patch_antenna = PatchAntenna(width, length)

    # Plot the radiation pattern along zero elevation.
    azimuth = np.linspace(-np.pi / 2, np.pi / 2, 360, endpoint=False)
    pattern = patch_antenna.calculate_pattern(azimuth=azimuth, elevation=0)
    plt.style.use("science")
    fig, ax = plt.subplots(
        figsize=(12, 8),
        subplot_kw={"projection": "polar"},
    )
    ax.plot(azimuth, constants.power2db(pattern + 1))
    ax.set_xlabel(r"Azimuth $\theta$")
    plt.show()

    # Plot the radiation pattern along zero azimuth.
    elevation = np.linspace(-np.pi / 2, np.pi / 2, 360, endpoint=False)
    pattern = patch_antenna.calculate_pattern(azimuth=0, elevation=elevation)
    plt.style.use("science")
    fig, ax = plt.subplots(
        figsize=(12, 8),
        subplot_kw={"projection": "polar"},
    )
    ax.plot(elevation, constants.power2db(pattern + 1))
    ax.set_xlabel(r"Elevation $\phi$")
    plt.show()


def main(argv):
    assert len(argv) == 1, argv

    plot_radiation_pattern_3d(FLAGS.width, FLAGS.length)
    plot_radiation_pattern_2d(FLAGS.width, FLAGS.length)


if __name__ == "__main__":
    flags.DEFINE_float("width",
                       0.5,
                       "Width in units of lambda.",
                       lower_bound=0.0)
    flags.DEFINE_float("length",
                       0.5,
                       "Length in units of lambda.",
                       lower_bound=0.0)

    app.run(main)
