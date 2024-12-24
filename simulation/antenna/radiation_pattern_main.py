"""Plots the radiation pattern of an antenna."""

import matplotlib.colors
import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from absl import app, flags
from matplotlib import cm

from simulation.antenna.radiation_pattern import RadiationPattern
from utils import constants
from utils.coordinates import SphericalCoordinates
from utils.visualization.color_maps import COLOR_MAPS

FLAGS = flags.FLAGS


def plot_radiation_pattern_3d_scatter(
        radiation_pattern: RadiationPattern) -> None:
    """Plots the 3D radiation pattern as a scatter plot.

    Args:
        radiation_pattern: Radiation pattern.
    """
    gain_db = radiation_pattern.df[radiation_pattern.gain_db_column]

    # Convert from spherical coordinates to Cartesian coordinates.
    r = gain_db - gain_db.min()
    x, y, z = radiation_pattern.transform_to_cartesian()

    # Generate the face colors.
    norm = matplotlib.colors.Normalize(
        vmin=np.min(gain_db),
        vmax=np.max(gain_db),
    )
    m = cm.ScalarMappable(
        cmap=COLOR_MAPS["parula"],
        norm=norm,
    )
    m.set_array([])

    # Plot the radiation pattern.
    plt.style.use("science")
    fig, ax = plt.subplots(
        figsize=(12, 6),
        subplot_kw={"projection": "3d"},
    )
    ax.scatter(
        x * r,
        y * r,
        z * r,
        c=r,
        cmap=COLOR_MAPS["parula"],
    )
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.set_zlabel(r"$z$")
    ax.set_aspect("equal", adjustable="box")
    ax.view_init(30, -45)
    plt.colorbar(m, ax=ax)
    plt.show()


def plot_radiation_pattern_3d(radiation_pattern: RadiationPattern) -> None:
    """Plots the interpolated 3D radiation pattern.

    Args:
        radiation_pattern: Radiation pattern.
    """
    azimuth = np.linspace(-np.pi, np.pi, 720, endpoint=False)
    elevation = np.linspace(-np.pi / 2, np.pi / 2, 360, endpoint=False)
    azimuth_mesh, elevation_mesh = np.meshgrid(
        azimuth,
        elevation,
        indexing="ij",
    )

    gain = radiation_pattern.calculate_pattern(azimuth_mesh, elevation_mesh)
    gain_db = constants.power2db(gain)

    # Convert from spherical coordinates to Cartesian coordinates.
    r = gain_db - np.min(gain_db)
    x, y, z = SphericalCoordinates.transform_to_cartesian_arrays(
        range=r,
        azimuth=azimuth_mesh,
        elevation=elevation_mesh,
    )

    # Generate the face colors.
    norm = matplotlib.colors.Normalize(
        vmin=np.min(gain_db),
        vmax=np.max(gain_db),
    )
    m = cm.ScalarMappable(
        cmap=COLOR_MAPS["parula"],
        norm=norm,
    )
    m.set_array([])

    # Plot the radiation pattern.
    plt.style.use("science")
    fig, ax = plt.subplots(
        figsize=(12, 6),
        subplot_kw={"projection": "3d"},
    )
    ax.plot_surface(
        x,
        y,
        z,
        facecolors=COLOR_MAPS["parula"](norm(gain_db)),
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


def plot_radiation_pattern_2d(radiation_pattern: RadiationPattern) -> None:
    """Plots the interpolated 2D radiation pattern along zero elevation and
    along zero azimuth.

    Args:
        radiation_pattern: Radiation pattern.
    """
    # Plot the radiation pattern along zero elevation.
    azimuth = np.linspace(-np.pi, np.pi, 720, endpoint=False)
    gain = radiation_pattern.calculate_pattern(azimuth=azimuth, elevation=0)
    plt.style.use("science")
    fig, ax = plt.subplots(
        figsize=(12, 6),
        subplot_kw={"projection": "polar"},
    )
    ax.plot(azimuth, constants.power2db(gain + 1))
    ax.set_xlabel("Azimuth")
    plt.show()

    # Plot the radiation pattern along zero azimuth.
    elevation = np.linspace(-np.pi / 2, np.pi / 2, 360, endpoint=False)
    gain = radiation_pattern.calculate_pattern(azimuth=0, elevation=elevation)
    plt.style.use("science")
    fig, ax = plt.subplots(
        figsize=(12, 6),
        subplot_kw={"projection": "polar"},
    )
    ax.plot(elevation, constants.power2db(gain + 1))
    ax.set_xlabel("Elevation")
    plt.show()


def main(argv):
    assert len(argv) == 1, argv

    radiation_pattern = RadiationPattern(FLAGS.data)
    plot_radiation_pattern_3d_scatter(radiation_pattern)
    plot_radiation_pattern_3d(radiation_pattern)
    plot_radiation_pattern_2d(radiation_pattern)


if __name__ == "__main__":
    flags.DEFINE_string(
        "data",
        "simulation/antenna/data/radiation_pattern_patch_antenna_24ghz_20mil.csv",
        "Radiation pattern CSV file.",
    )

    app.run(main)
