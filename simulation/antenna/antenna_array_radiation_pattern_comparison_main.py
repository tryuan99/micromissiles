"""Compares the radiation patterns of multiple antenna arrays."""

import google.protobuf
import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from absl import app, flags
from matplotlib import artist
from matplotlib.lines import Line2D

from simulation.antenna.antenna_array import (AntennaArray,
                                              AntennaArrayBeamSteer)
from simulation.antenna.proto.antenna_array_config_pb2 import \
    AntennaArrayConfig
from utils import constants
from utils.visualization.animator import Animator2D

FLAGS = flags.FLAGS

# Animation interval in milliseconds.
ANIMATION_INTERVAL = 20  # milliseconds


def plot_antenna_array_elements(
    arrays: list[AntennaArray],
    labels: list[str],
) -> None:
    """Plots the antenna array elements of the arrays.

    Args:
        arrays: Antenna arrays.
        labels: Antenna array labels.
    """
    # Plot the antenna array elements.
    plt.style.use("science")
    fig, ax = plt.subplots(
        figsize=(12, 6),
        subplot_kw={"projection": "3d"},
    )
    for array_index, (array, label) in enumerate(zip(arrays, labels)):
        element_coordinates = np.array(
            [element.coordinates() for element in array.elements])
        ax.scatter(
            element_coordinates[:, 0],
            element_coordinates[:, 1],
            element_coordinates[:, 2],
            s=120,
            c=f"C{array_index}",
            marker="^",
            alpha=0.4,
            label=label,
        )
        repeated_element_coordinates = element_coordinates.repeat(3, axis=0)
        element_axes = np.array([[
            element.boresight(),
            element.right(),
            element.vertical(),
        ] for element in array.elements])
        reshaped_element_axes = element_axes.reshape(-1, 3)
        ax.quiver(
            repeated_element_coordinates[:, 0],
            repeated_element_coordinates[:, 1],
            repeated_element_coordinates[:, 2],
            reshaped_element_axes[:, 0],
            reshaped_element_axes[:, 1],
            reshaped_element_axes[:, 2],
            length=0.1,
            normalize=True,
            color=f"C{array_index}",
            alpha=0.4,
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
    ax.legend()
    plt.show()


def plot_antenna_array_radiation_pattern_2d(
    arrays: list[AntennaArray],
    labels: list[str],
    beam_steer: AntennaArrayBeamSteer,
) -> None:
    """Plots the 2D radiation patterns of the antenna arrays along the desired
    azimuth and elevation.

    Args:
        arrays: Antenna arrays.
        labels: Antenna array labels.
        beam_steer: Antenna beam steering direction.
    """
    # Plot the radiation patterns along zero elevation.
    azimuth = np.linspace(-np.pi, np.pi, 720, endpoint=False)
    plt.style.use("science")
    fig, ax = plt.subplots(
        figsize=(12, 6),
        subplot_kw={"projection": "polar"},
    )
    for array, label in zip(arrays, labels):
        radiation_pattern = array.calculate_radiation_pattern(
            beam_steer,
            azimuth,
            beam_steer.elevation,
        )
        radiation_pattern_db = (
            constants.power2db(np.abs(radiation_pattern) + 1))
        ax.plot(azimuth, radiation_pattern_db, label=label)
    ax.set_xlabel("Azimuth")
    ax.legend()
    plt.show()

    # Plot the radiation patterns along zero azimuth.
    elevation = np.linspace(-np.pi / 2, np.pi / 2, 360, endpoint=False)
    plt.style.use("science")
    fig, ax = plt.subplots(
        figsize=(12, 6),
        subplot_kw={"projection": "polar"},
    )
    for array, label in zip(arrays, labels):
        radiation_pattern = array.calculate_radiation_pattern(
            beam_steer,
            beam_steer.azimuth,
            elevation,
        )
        radiation_pattern_db = (
            constants.power2db(np.abs(radiation_pattern) + 1))
        ax.plot(elevation, radiation_pattern_db, label=label)
    ax.set_xlabel("Elevation")
    ax.legend()
    plt.show()


def animate_antenna_array_radiation_pattern_2d(
    arrays: list[AntennaArray],
    labels: list[str],
) -> None:
    """Animates the 2D radiation patterns of the antenna arrays along zero
    azimuth and zero elevation.

    Args:
        arrays: Antenna arrays.
        labels: Antenna array labels.
    """
    # Sweep the azimuth.
    azimuth_sweep = np.linspace(-np.pi / 2, np.pi / 2, 180, endpoint=False)
    azimuth = np.linspace(-np.pi / 2, np.pi / 2, 360, endpoint=False)

    # Configure and run the animation.
    animator = Animator2D()

    def add_artist(array: AntennaArray, label: str, index: int) -> None:
        """Adds an artist for the radiation pattern of the antenna array.

        Args:
            array: Antenna array.
            label: Antenna array label.
            index: Antenna array index.
        """
        line = Line2D(
            azimuth,
            np.zeros(len(azimuth)),
            color=f"C{index}",
        )

        def update_line(line: artist.Artist, frame: float) -> artist.Artist:
            """Returns the line at each frame.

            Args:
                line: Line.
                frame: Azimuth to plot.
            """
            radiation_pattern = array.calculate_radiation_pattern(
                AntennaArrayBeamSteer(azimuth=frame, elevation=0),
                azimuth=azimuth,
                elevation=0,
            )
            line.set_data(
                azimuth,
                constants.power2db(np.abs(radiation_pattern)),
            )
            return line

        animator.add_artist(line, update_line, label)

    max_gain = -np.inf
    for array_index, (array, label) in enumerate(zip(arrays, labels)):
        add_artist(array, label, array_index)

        # Find the maximum gain.
        radiation_pattern = array.calculate_radiation_pattern(
            AntennaArrayBeamSteer(azimuth=0, elevation=0),
            azimuth=azimuth,
            elevation=0,
        )
        max_gain = max(np.max(np.abs(radiation_pattern)), max_gain)
    animator.set_labels("Azimuth [rad]", "Magnitude [dB]")
    animator.set_limits(
        xlim=(np.min(azimuth), np.max(azimuth)),
        ylim=(-20, constants.power2db(max_gain) + 5),
    )

    def update_title(azimuth: float) -> str:
        """Returns the title at each frame.

        Args:
            azimuth: Azimuth to plot.
        """
        return rf"Radiation pattern (azimuth = ${azimuth}$ rad)"

    animator.set_title("Radiation pattern", update_title)
    animator.configure_animation(azimuth_sweep, ANIMATION_INTERVAL)
    animator.show()

    # Sweep the elevation.
    elevation_sweep = np.linspace(-np.pi / 2, np.pi / 2, 180, endpoint=False)
    elevation = np.linspace(-np.pi / 2, np.pi / 2, 360, endpoint=False)

    # Configure and run the animation.
    animator = Animator2D()

    def add_artist(array: AntennaArray, label: str, index: int) -> None:
        """Adds an artist for the radiation pattern of the antenna array.

        Args:
            array: Antenna array.
            label: Antenna array label.
            index: Antenna array index.
        """
        line = Line2D(
            elevation,
            np.zeros(len(elevation)),
            color=f"C{index}",
        )

        def update_line(line: artist.Artist, frame: float) -> artist.Artist:
            """Returns the line at each frame.

            Args:
                line: Line.
                frame: Elevation to plot.
            """
            radiation_pattern = array.calculate_radiation_pattern(
                AntennaArrayBeamSteer(azimuth=0, elevation=frame),
                azimuth=0,
                elevation=elevation,
            )
            line.set_data(
                elevation,
                constants.power2db(np.abs(radiation_pattern)),
            )
            return line

        animator.add_artist(line, update_line, label)

    max_gain = -np.inf
    for array_index, (array, label) in enumerate(zip(arrays, labels)):
        add_artist(array, label, array_index)

        # Find the maximum gain.
        radiation_pattern = array.calculate_radiation_pattern(
            AntennaArrayBeamSteer(azimuth=0, elevation=0),
            azimuth=0,
            elevation=elevation,
        )
        max_gain = max(np.max(np.abs(radiation_pattern)), max_gain)
    animator.set_labels("Elevation [rad]", "Magnitude [dB]")
    animator.set_limits(
        xlim=(np.min(elevation), np.max(elevation)),
        ylim=(-20, constants.power2db(max_gain) + 5),
    )

    def update_title(elevation: float) -> str:
        """Returns the title at each frame.

        Args:
            elevation: Elevation to plot.
        """
        return rf"Radiation pattern (elevation = ${elevation}$ rad)"

    animator.set_title("Radiation pattern", update_title)
    animator.configure_animation(elevation_sweep, ANIMATION_INTERVAL)
    animator.show()


def main(argv):
    assert len(argv) == 1, argv

    # Parse the antenna array configurations and create the antenna arrays.
    arrays = []
    for config in FLAGS.configs:
        with open(config, "r") as antenna_array_config_file:
            antenna_array_config = google.protobuf.text_format.Parse(
                antenna_array_config_file.read(), AntennaArrayConfig())
        arrays.append(AntennaArray.create(antenna_array_config))
    beam_steer = AntennaArrayBeamSteer(
        azimuth=FLAGS.azimuth,
        elevation=FLAGS.elevation,
    )
    plot_antenna_array_elements(arrays, FLAGS.labels)
    plot_antenna_array_radiation_pattern_2d(arrays, FLAGS.labels, beam_steer)
    animate_antenna_array_radiation_pattern_2d(arrays, FLAGS.labels)


if __name__ == "__main__":
    flags.DEFINE_multi_string("configs", [
        "simulation/antenna/configs/ula_4_patch_antenna_24ghz.pbtxt",
        "simulation/antenna/configs/ula_4_rotated_outer_patch_antenna_24ghz.pbtxt",
        "simulation/antenna/configs/ula_4_rotated_outer_recessed_patch_antenna_24ghz.pbtxt",
    ], "Antenna array configurations.")
    flags.DEFINE_multi_string("labels", [
        "4-element ULA",
        "4-element ULA with rotated outer elements",
        "4-element ULA with rotated and recessed outer elements",
        "4-element ULA with rotated and recessed elements",
    ], "Antenna array labels.")
    flags.DEFINE_float("azimuth", 0, "Azimuth in radians.")
    flags.DEFINE_float("elevation", 0, "Elevation in radians.")

    app.run(main)
