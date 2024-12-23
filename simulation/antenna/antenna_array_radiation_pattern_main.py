"""Plots the radiation pattern of an antenna array."""

import google.protobuf
import matplotlib.colors
import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from absl import app, flags
from matplotlib import cm

from simulation.antenna.antenna_array import (AntennaArray,
                                              AntennaArrayBeamSteer,
                                              AntennaArrayElement)
from simulation.antenna.isotropic_antenna import IsotropicAntenna
from simulation.antenna.proto.antenna_array_config_pb2 import \
    AntennaArrayConfig
from simulation.antenna.radiation_pattern import RadiationPattern
from utils import constants
from utils.coordinates import SphericalCoordinates
from utils.visualization.color_maps import COLOR_MAPS

FLAGS = flags.FLAGS


def plot_antenna_array_elements(array: AntennaArray) -> None:
    """Plots the antenna array elements.

    Args:
        array: Antenna array.
    """
    # Plot the antenna array elements.
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(
        figsize=(12, 6),
        subplot_kw={"projection": "3d"},
    )
    for element in array.elements:
        coordinates = element.coordinates()
        ax.scatter(
            *coordinates,
            s=120,
            c="C0",
            marker="^",
            alpha=0.5,
        )
        ax.quiver(
            *coordinates,
            *element.boresight(),
            length=0.1,
            normalize=True,
            color="C0",
        )
        ax.quiver(
            *coordinates,
            *element.right(),
            length=0.1,
            normalize=True,
            color="C1",
        )
        ax.quiver(
            *coordinates,
            *element.vertical(),
            length=0.1,
            normalize=True,
            color="C2",
        )
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.set_zlabel(r"$z$")
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    zmin, zmax = ax.get_zlim()
    ax.set_xlim(min(xmin, -0.1), xmax)
    ax.set_ylim(ymin, max(ymax, 0.1))
    ax.set_zlim(zmin, max(zmax, 0.1))
    ax.view_init(30, -45, vertical_axis="y")
    plt.show()


def plot_antenna_array_radiation_pattern(
    array: AntennaArray,
    beam_steer: AntennaArrayBeamSteer,
) -> None:
    """Plots the radiation pattern of an antenna array.

    Args:
        array: Antenna array.
        beam_steer: Antenna beam steering direction.
    """
    # Calculate the radiation pattern of the antenna array.
    azimuth = np.linspace(-np.pi, np.pi, 720, endpoint=False)
    elevation = np.linspace(-np.pi / 2, np.pi / 2, 360, endpoint=False)
    azimuth_mesh, elevation_mesh = np.meshgrid(
        azimuth,
        elevation,
        indexing="ij",
    )
    radiation_pattern = array.calculate_radiation_pattern(
        beam_steer,
        azimuth_mesh,
        elevation_mesh,
    )
    radiation_pattern_db = constants.power2db(np.abs(radiation_pattern) + 1)
    r = radiation_pattern_db - np.min(radiation_pattern_db)
    x, y, z = SphericalCoordinates.transform_to_cartesian_arrays(
        range=r,
        azimuth=azimuth_mesh,
        elevation=elevation_mesh,
    )

    # Generate the face colors.
    norm = matplotlib.colors.Normalize(
        vmin=np.min(radiation_pattern_db),
        vmax=np.max(radiation_pattern_db),
    )
    m = cm.ScalarMappable(
        cmap=COLOR_MAPS["parula"],
        norm=norm,
    )
    m.set_array([])

    # Plot the radiation pattern of the antenna array.
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(
        figsize=(12, 6),
        subplot_kw={"projection": "3d"},
    )
    ax.plot_surface(
        x,
        y,
        z,
        facecolors=COLOR_MAPS["parula"](norm(radiation_pattern_db)),
        shade=False,
        antialiased=False,
    )
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.set_zlabel(r"$z$")
    ax.view_init(30, -45, vertical_axis="y")
    plt.colorbar(m, ax=ax)
    plt.show()


def main(argv):
    assert len(argv) == 1, argv

    # Parse the antenna array configuration and create the antenna array.
    with open(FLAGS.config, "r") as antenna_array_config_file:
        antenna_array_config = google.protobuf.text_format.Parse(
            antenna_array_config_file.read(), AntennaArrayConfig())
    array = AntennaArray.create(antenna_array_config)
    beam_steer = AntennaArrayBeamSteer(
        azimuth=FLAGS.azimuth,
        elevation=FLAGS.elevation,
    )
    plot_antenna_array_elements(array)
    plot_antenna_array_radiation_pattern(array, beam_steer)


if __name__ == "__main__":
    flags.DEFINE_string(
        "config", "simulation/antenna/configs/ula_4_patch_antenna_24ghz.pbtxt",
        "Antenna array configuration.")
    flags.DEFINE_float("azimuth", 0, "Azimuth in radians.")
    flags.DEFINE_float("elevation", 0, "Elevation in radians.")

    app.run(main)
