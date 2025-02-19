"""Plots the radiation pattern of an antenna array."""

import google.protobuf
import matplotlib.colors
import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from absl import app, flags
from matplotlib import artist, cm
from matplotlib.lines import Line2D

from simulation.antenna.antenna_array import (AntennaArray,
                                              AntennaArrayBeamSteer)
from simulation.antenna.proto.antenna_array_config_pb2 import \
    AntennaArrayConfig
from utils.coordinates import SphericalCoordinates
from utils.visualization.animator import Animator2D, Animator3D
from utils.visualization.color_maps import COLOR_MAPS

FLAGS = flags.FLAGS

# Animation interval in milliseconds.
ANIMATION_INTERVAL = 20  # milliseconds


def plot_antenna_array_radiation_pattern_3d(
    array: AntennaArray,
    beam_steer: AntennaArrayBeamSteer,
) -> None:
    """Plots the 3D radiation pattern of an antenna array.

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
    r = radiation_pattern.db() - radiation_pattern.min_db()
    x, y, z = SphericalCoordinates.transform_to_cartesian_arrays(
        range=r,
        azimuth=azimuth_mesh,
        elevation=elevation_mesh,
    )

    # Generate the face colors.
    norm = matplotlib.colors.Normalize(
        vmin=radiation_pattern.min_db(),
        vmax=radiation_pattern.max_db(),
    )
    m = cm.ScalarMappable(
        cmap=COLOR_MAPS["parula"],
        norm=norm,
    )
    m.set_array([])

    # Plot the radiation pattern of the antenna array.
    plt.style.use("science")
    fig, ax = plt.subplots(
        figsize=(12, 6),
        subplot_kw={"projection": "3d"},
    )
    ax.plot_surface(
        x,
        y,
        z,
        facecolors=COLOR_MAPS["parula"](norm(radiation_pattern.db())),
        shade=False,
        antialiased=False,
    )
    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$y$")
    ax.set_zlabel(r"$z$")
    ax.view_init(30, -45, vertical_axis="y")
    plt.colorbar(m, ax=ax)
    plt.show()


def plot_antenna_array_radiation_pattern_2d(
    array: AntennaArray,
    beam_steer: AntennaArrayBeamSteer,
) -> None:
    """Plots the 2D radiation pattern of an antenna array along the desired
    azimuth and elevation.

    Args:
        array: Antenna array.
        beam_steer: Antenna beam steering direction.
    """
    # Plot the radiation pattern along zero elevation.
    azimuth = np.linspace(-np.pi, np.pi, 720, endpoint=False)
    radiation_pattern = array.calculate_radiation_pattern(
        beam_steer,
        azimuth,
        beam_steer.elevation,
    )
    plt.style.use("science")
    fig, ax = plt.subplots(
        figsize=(12, 6),
        subplot_kw={"projection": "polar"},
    )
    ax.plot(azimuth, radiation_pattern.db())
    ax.axvline(
        beam_steer.azimuth,
        color="red",
        linestyle="--",
    )
    ax.set_xlabel("Azimuth")
    plt.show()

    # Plot the radiation pattern along zero azimuth.
    elevation = np.linspace(-np.pi / 2, np.pi / 2, 360, endpoint=False)
    radiation_pattern = array.calculate_radiation_pattern(
        beam_steer,
        beam_steer.azimuth,
        elevation,
    )
    plt.style.use("science")
    fig, ax = plt.subplots(
        figsize=(12, 6),
        subplot_kw={"projection": "polar"},
    )
    ax.plot(elevation, radiation_pattern.db())
    ax.axvline(
        beam_steer.elevation,
        color="red",
        linestyle="--",
    )
    ax.set_xlabel("Elevation")
    plt.show()


def animate_antenna_array_radiation_pattern_3d(
    array: AntennaArray,
    beam_steer: AntennaArrayBeamSteer,
) -> None:
    """Animates the 3D radiation pattern of an antenna array.

    Args:
        array: Antenna array.
        beam_steer: Antenna beem steering direction.
    """
    azimuth = np.linspace(-np.pi, np.pi, 720, endpoint=False)
    elevation = np.linspace(-np.pi / 2, np.pi / 2, 360, endpoint=False)
    azimuth_mesh, elevation_mesh = np.meshgrid(
        azimuth,
        elevation,
        indexing="ij",
    )

    # Sweep the azimuth.
    azimuth_sweep = np.linspace(-np.pi / 2, np.pi / 2, 180, endpoint=False)
    radiation_pattern = array.calculate_radiation_pattern(
        AntennaArrayBeamSteer(azimuth=0, elevation=beam_steer.elevation),
        azimuth_mesh,
        elevation_mesh,
    )
    max_radius = radiation_pattern.max_db() - radiation_pattern.min_db()

    # Generate the face colors.
    norm = matplotlib.colors.Normalize(
        vmin=radiation_pattern.min_db(),
        vmax=radiation_pattern.max_db(),
    )
    m = cm.ScalarMappable(
        cmap=COLOR_MAPS["parula"],
        norm=norm,
    )
    m.set_array([])

    # Configure and run the animation.
    animator = Animator3D()

    def update_surface(surf: artist.Artist, frame: float) -> None:
        """Returns the surface at each frame.

        Args:
            surf: Surface.
            frame: Azimuth to plot.
        """
        radiation_pattern = array.calculate_radiation_pattern(
            AntennaArrayBeamSteer(
                azimuth=frame,
                elevation=beam_steer.elevation,
            ),
            azimuth_mesh,
            elevation_mesh,
        )
        r = radiation_pattern.db() - radiation_pattern.min_db()
        x, y, z = SphericalCoordinates.transform_to_cartesian_arrays(
            range=r,
            azimuth=azimuth_mesh,
            elevation=elevation_mesh,
        )

        surf.remove()
        return animator.axes().plot_surface(
            x,
            y,
            z,
            facecolors=COLOR_MAPS["parula"](norm(radiation_pattern.db())),
            shade=False,
            antialiased=False,
        )

    animator.add_artist(artist.Artist(), update_surface)
    animator.add_colorbar(m)
    animator.set_labels(r"$x$", r"$y$", r"$z$")
    animator.set_limits(
        xlim=(-max_radius, max_radius),
        ylim=(-max_radius, max_radius),
        zlim=(-1, max_radius),
    )

    def update_title(azimuth: float) -> str:
        """Returns the title at each frame.

        Args:
            azimuth: Azimuth to plot.
        """
        return rf"Radiation pattern (azimuth = ${azimuth}$ rad)"

    animator.set_title("Radiation pattern", update_title)
    animator.view_init(30, -45, vertical_axis="y")
    animator.configure_animation(azimuth_sweep, ANIMATION_INTERVAL)
    animator.show()

    # Sweep the elevation.
    elevation_sweep = np.linspace(np.pi / 2, -np.pi / 2, 180, endpoint=False)
    radiation_pattern = array.calculate_radiation_pattern(
        AntennaArrayBeamSteer(azimuth=beam_steer.azimuth, elevation=0),
        azimuth_mesh,
        elevation_mesh,
    )
    max_radius = radiation_pattern.max_db() - radiation_pattern.min_db()

    # Generate the face colors.
    norm = matplotlib.colors.Normalize(
        vmin=radiation_pattern.min_db(),
        vmax=radiation_pattern.max_db(),
    )
    m = cm.ScalarMappable(
        cmap=COLOR_MAPS["parula"],
        norm=norm,
    )
    m.set_array([])

    # Configure and run the animation.
    animator = Animator3D()

    def update_surface(surf: artist.Artist, frame: float) -> None:
        """Returns the surface at each frame.

        Args:
            surf: Surface.
            frame: Elevation to plot.
        """
        radiation_pattern = array.calculate_radiation_pattern(
            AntennaArrayBeamSteer(
                azimuth=beam_steer.azimuth,
                elevation=frame,
            ),
            azimuth_mesh,
            elevation_mesh,
        )
        r = radiation_pattern.db() - radiation_pattern.min_db()
        x, y, z = SphericalCoordinates.transform_to_cartesian_arrays(
            range=r,
            azimuth=azimuth_mesh,
            elevation=elevation_mesh,
        )

        surf.remove()
        return animator.axes().plot_surface(
            x,
            y,
            z,
            facecolors=COLOR_MAPS["parula"](norm(radiation_pattern.db())),
            shade=False,
            antialiased=False,
        )

    animator.add_artist(artist.Artist(), update_surface)
    animator.add_colorbar(m)
    animator.set_labels(r"$x$", r"$y$", r"$z$")
    animator.set_limits(
        xlim=(-max_radius, max_radius),
        ylim=(-max_radius, max_radius),
        zlim=(-1, max_radius),
    )

    def update_title(elevation: float) -> str:
        """Returns the title at each frame.

        Args:
            elevation: Elevation to plot.
        """
        return rf"Radiation pattern (elevation = ${elevation}$ rad)"

    animator.set_title("Radiation pattern", update_title)
    animator.view_init(30, -45, vertical_axis="y")
    animator.configure_animation(elevation_sweep, ANIMATION_INTERVAL)
    animator.show()


def animate_antenna_array_radiation_pattern_2d(
    array: AntennaArray,
    beam_steer: AntennaArrayBeamSteer,
) -> None:
    """Animates the 2D radiation pattern of an antenna array along zero azimuth
    and zero elevation.

    Args:
        array: Antenna array.
        beam_steer: Antenna beem steering direction.
    """
    # Sweep the azimuth.
    azimuth_sweep = np.linspace(-np.pi / 2, np.pi / 2, 180, endpoint=False)
    azimuth = np.linspace(-np.pi, np.pi, 720, endpoint=False)

    # Configure and run the animation.
    animator = Animator2D()
    line = Line2D(azimuth, np.zeros(len(azimuth)))

    def update_line(line: artist.Artist, frame: float) -> artist.Artist:
        """Returns the line at each frame.

        Args:
            line: Line.
            frame: Azimuth to plot.
        """
        radiation_pattern = array.calculate_radiation_pattern(
            AntennaArrayBeamSteer(
                azimuth=frame,
                elevation=beam_steer.elevation,
            ),
            azimuth=azimuth,
            elevation=beam_steer.elevation,
        )
        line.set_data(azimuth, radiation_pattern.db(log_plus_one=False))
        return line

    animator.add_artist(line, update_line)

    # Add a line to mark the current azimuth.
    radiation_pattern = array.calculate_radiation_pattern(
        AntennaArrayBeamSteer(azimuth=0, elevation=beam_steer.elevation),
        azimuth=azimuth,
        elevation=beam_steer.elevation,
    )
    ylim = (-20, radiation_pattern.max_db() + 5)
    azimuth_line = Line2D(
        np.zeros(2),
        ylim,
        color="red",
        linestyle="--",
    )

    def update_azimuth_line(line: artist.Artist, frame: float) -> artist.Artist:
        """Returns the azimuth line at each frame.

            Args:
                line: Line.
                frame: Azimuth to plot.
            """
        line.set_xdata([frame, frame])
        return line

    animator.add_artist(azimuth_line, update_azimuth_line)

    animator.set_labels("Azimuth [rad]", "Magnitude [dB]")
    animator.set_limits(
        xlim=(np.min(azimuth), np.max(azimuth)),
        ylim=ylim,
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
    line = Line2D(elevation, np.zeros(len(elevation)))

    def update_line(line: artist.Artist, frame: float) -> artist.Artist:
        """Returns the line at each frame.

        Args:
            line: Line.
            frame: Elevation to plot.
        """
        radiation_pattern = array.calculate_radiation_pattern(
            AntennaArrayBeamSteer(
                azimuth=beam_steer.azimuth,
                elevation=frame,
            ),
            azimuth=beam_steer.azimuth,
            elevation=elevation,
        )
        line.set_data(elevation, radiation_pattern.db(log_plus_one=False))
        return line

    animator.add_artist(line, update_line)

    # Add a line to mark the current elevation.
    radiation_pattern = array.calculate_radiation_pattern(
        AntennaArrayBeamSteer(azimuth=beam_steer.azimuth, elevation=0),
        azimuth=beam_steer.azimuth,
        elevation=elevation,
    )
    ylim = (-20, radiation_pattern.max_db() + 5)
    elevation_line = Line2D(
        np.zeros(2),
        ylim,
        color="red",
        linestyle="--",
    )

    def update_elevation_line(line: artist.Artist,
                              frame: float) -> artist.Artist:
        """Returns the elevation line at each frame.

            Args:
                line: Line.
                frame: Elevation to plot.
            """
        line.set_xdata([frame, frame])
        return line

    animator.add_artist(elevation_line, update_elevation_line)

    animator.set_labels("Elevation [rad]", "Magnitude [dB]")
    animator.set_limits(
        xlim=(np.min(elevation), np.max(elevation)),
        ylim=ylim,
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

    # Parse the antenna array configuration and create the antenna array.
    with open(FLAGS.config, "r") as antenna_array_config_file:
        antenna_array_config = google.protobuf.text_format.Parse(
            antenna_array_config_file.read(), AntennaArrayConfig())
    array = AntennaArray.create(antenna_array_config)
    beam_steer = AntennaArrayBeamSteer(
        azimuth=FLAGS.azimuth,
        elevation=FLAGS.elevation,
    )

    plot_antenna_array_radiation_pattern_3d(array, beam_steer)
    plot_antenna_array_radiation_pattern_2d(array, beam_steer)
    animate_antenna_array_radiation_pattern_3d(array, beam_steer)
    animate_antenna_array_radiation_pattern_2d(array, beam_steer)


if __name__ == "__main__":
    flags.DEFINE_string(
        "config",
        "simulation/antenna/configs/ula_4_patch_antenna_24ghz.pbtxt",
        "Antenna array configuration.",
    )
    flags.DEFINE_float("azimuth", 0, "Azimuth in radians.")
    flags.DEFINE_float("elevation", 0, "Elevation in radians.")

    app.run(main)
