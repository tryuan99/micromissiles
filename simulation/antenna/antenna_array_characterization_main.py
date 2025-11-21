"""Characterizes the antenna array in terms of main lobe width and sidelobe
level.
"""

import google.protobuf
import matplotlib.pyplot as plt
import numpy as np
from absl import app, flags

import utils.visualization.mpl_config
from simulation.antenna.antenna_array import (AntennaArray,
                                              AntennaArrayBeamSteer)
from simulation.antenna.proto.antenna_array_config_pb2 import \
    AntennaArrayConfig
from utils.visualization.color_maps import COLOR_MAPS

FLAGS = flags.FLAGS


def plot_antenna_array_main_lobe_width_3d(array: AntennaArray) -> None:
    """Plots the main lobe width over azimuth and elevation of an antenna
    array.

    Args:
        array: Antenna array.
    """
    azimuth_sweep = np.linspace(-np.pi / 2, np.pi / 2, 18, endpoint=False)
    elevation_sweep = np.linspace(-np.pi / 2, np.pi / 2, 18, endpoint=False)
    azimuth_values = np.linspace(-np.pi, np.pi, 360, endpoint=False)
    elevation_values = np.linspace(-np.pi, np.pi, 360, endpoint=False)
    azimuth_mesh, elevation_mesh = np.meshgrid(
        azimuth_values,
        elevation_values,
        indexing="ij",
    )

    azimuth_main_lobe_widths = np.zeros(
        (len(azimuth_sweep), len(elevation_sweep)))
    elevation_main_lobe_widths = np.zeros(
        (len(azimuth_sweep), len(elevation_sweep)))
    for azimuth_index, azimuth in enumerate(azimuth_sweep):
        for elevation_index, elevation in enumerate(elevation_sweep):
            beam_steer = AntennaArrayBeamSteer(azimuth, elevation)
            radiation_pattern = array.calculate_radiation_pattern(
                beam_steer,
                azimuth_mesh,
                elevation_mesh,
            )
            azimuth_peak_index = np.argmin(np.abs(azimuth_values - azimuth))
            elevation_peak_index = np.argmin(
                np.abs(elevation_values - elevation))
            main_lobe_widths = radiation_pattern.main_lobe_width(
                np.array([
                    azimuth_peak_index,
                    elevation_peak_index,
                ]))
            (
                azimuth_main_lobe_widths[azimuth_index, elevation_index],
                elevation_main_lobe_widths[azimuth_index, elevation_index],
            ) = main_lobe_widths

    # Plot the main lobe width along the azimuth axis as a 3D surface.
    fig, ax = plt.subplots(
        figsize=(12, 6),
        subplot_kw={"projection": "3d"},
    )
    surf = ax.plot_surface(
        *np.meshgrid(azimuth_sweep, elevation_sweep, indexing="ij"),
        azimuth_main_lobe_widths,
        cmap=COLOR_MAPS["parula"],
        antialiased=False,
    )
    ax.set_xlabel("Azimuth [rad]")
    ax.set_ylabel("Elevation [rad]")
    ax.set_zlabel("Azimuth main lobe width [rad]")
    ax.view_init(30, -45)
    plt.colorbar(surf)
    plt.show()

    # Plot the main lobe width along the azimuth axis as a heatmap.
    fig, ax = plt.subplots(figsize=(12, 6))
    image = ax.imshow(
        azimuth_main_lobe_widths,
        cmap=COLOR_MAPS["parula"],
        origin="lower",
        extent=(
            np.min(azimuth_sweep) - np.diff(azimuth_sweep)[0] / 2,
            np.max(azimuth_sweep) - np.diff(azimuth_sweep)[0] / 2,
            np.min(elevation_sweep) - np.diff(elevation_sweep)[0] / 2,
            np.max(elevation_sweep) - np.diff(elevation_sweep)[0] / 2,
        ),
    )
    ax.set_xlabel("Azimuth [rad]")
    ax.set_ylabel("Elevation [rad]")
    plt.colorbar(image, label="Azimuth main lobe width [rad]")
    plt.show()

    # Plot the main lobe width along the elevation axis as a 3D surface.
    fig, ax = plt.subplots(
        figsize=(12, 6),
        subplot_kw={"projection": "3d"},
    )
    surf = ax.plot_surface(
        *np.meshgrid(azimuth_sweep, elevation_sweep, indexing="ij"),
        elevation_main_lobe_widths,
        cmap=COLOR_MAPS["parula"],
        antialiased=False,
    )
    ax.set_xlabel("Azimuth [rad]")
    ax.set_ylabel("Elevation [rad]")
    ax.set_zlabel("Elevation main lobe width [rad]")
    ax.view_init(30, -45)
    plt.colorbar(surf)
    plt.show()

    # Plot the main lobe width along the elevation axis as a heatmap.
    fig, ax = plt.subplots(figsize=(12, 6))
    image = ax.imshow(
        elevation_main_lobe_widths,
        cmap=COLOR_MAPS["parula"],
        origin="lower",
        extent=(
            np.min(azimuth_sweep) - 0.5,
            np.max(azimuth_sweep) - 0.5,
            np.min(elevation_sweep) - 0.5,
            np.max(elevation_sweep) - 0.5,
        ),
    )
    ax.set_xlabel("Azimuth [rad]")
    ax.set_ylabel("Elevation [rad]")
    plt.colorbar(image, label="Elevation main lobe width [rad]")
    plt.show()


def plot_antenna_array_main_lobe_width_2d(
    array: AntennaArray,
    beam_steer: AntennaArrayBeamSteer,
) -> None:
    """Plots the main lobe width over azimuth and elevation separately of an
    antenna array.

    Args:
        array: Antenna array.
        beam_steer: Antenna beam steering direction.
    """
    # Plot the main lobe width over azimuth.
    azimuth_sweep = np.linspace(-np.pi / 2, np.pi / 2, 180, endpoint=False)
    azimuth_values = np.linspace(-np.pi, np.pi, 360, endpoint=False)

    azimuth_main_lobe_widths = np.zeros(azimuth_sweep.shape)
    for azimuth_index, azimuth in enumerate(azimuth_sweep):
        azimuth_beam_steer = AntennaArrayBeamSteer(
            azimuth,
            beam_steer.elevation,
        )
        radiation_pattern = array.calculate_radiation_pattern(
            azimuth_beam_steer,
            azimuth_values,
            azimuth_beam_steer.elevation,
        )
        azimuth_peak_index = np.argmin(np.abs(azimuth_values - azimuth))
        main_lobe_width = radiation_pattern.main_lobe_width(azimuth_peak_index)
        azimuth_main_lobe_widths[azimuth_index] = main_lobe_width

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(azimuth_sweep, azimuth_main_lobe_widths)
    ax.set_xlabel("Azimuth [rad]")
    ax.set_ylabel("Azimuth main lobe width [rad]")
    plt.show()

    # Plot the main lobe width over elevation.
    elevation_sweep = np.linspace(-np.pi / 2, np.pi / 2, 180, endpoint=False)
    elevation_values = np.linspace(-np.pi, np.pi, 360, endpoint=False)

    elevation_main_lobe_widths = np.zeros(elevation_sweep.shape)
    for elevation_index, elevation in enumerate(elevation_sweep):
        elevation_beam_steer = AntennaArrayBeamSteer(
            beam_steer.azimuth,
            elevation,
        )
        radiation_pattern = array.calculate_radiation_pattern(
            elevation_beam_steer,
            elevation_beam_steer.azimuth,
            elevation_values,
        )
        elevation_peak_index = np.argmin(np.abs(elevation_values - elevation))
        main_lobe_width = radiation_pattern.main_lobe_width(
            elevation_peak_index)
        elevation_main_lobe_widths[elevation_index] = main_lobe_width

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(elevation_sweep, elevation_main_lobe_widths)
    ax.set_xlabel("Elevation [rad]")
    ax.set_ylabel("Elevation main lobe width [rad]")
    plt.show()


def plot_antenna_array_sidelobe_level_3d(array: AntennaArray) -> None:
    """Plots the sidelobe level over azimuth and elevation of an antenna array.

    Args:
        array: Antenna array.
    """
    azimuth_sweep = np.linspace(-np.pi / 2, np.pi / 2, 18, endpoint=False)
    elevation_sweep = np.linspace(-np.pi / 2, np.pi / 2, 18, endpoint=False)
    azimuth_values = np.linspace(-np.pi, np.pi, 360, endpoint=False)
    elevation_values = np.linspace(-np.pi / 2, np.pi / 2, 180, endpoint=False)
    azimuth_mesh, elevation_mesh = np.meshgrid(
        azimuth_values,
        elevation_values,
        indexing="ij",
    )

    sidelobe_levels = np.zeros((len(azimuth_sweep), len(elevation_sweep)))
    for azimuth_index, azimuth in enumerate(azimuth_sweep):
        for elevation_index, elevation in enumerate(elevation_sweep):
            beam_steer = AntennaArrayBeamSteer(azimuth, elevation)
            radiation_pattern = array.calculate_radiation_pattern(
                beam_steer,
                azimuth_mesh,
                elevation_mesh,
            )
            azimuth_peak_index = np.argmin(np.abs(azimuth_values - azimuth))
            elevation_peak_index = np.argmin(
                np.abs(elevation_values - elevation))
            sidelobe_level = radiation_pattern.sidelobe_level(
                np.array([
                    azimuth_peak_index,
                    elevation_peak_index,
                ]))
            sidelobe_levels[azimuth_index, elevation_index] = sidelobe_level

    # Plot the sidelobe level as a 3D surface.
    fig, ax = plt.subplots(
        figsize=(12, 6),
        subplot_kw={"projection": "3d"},
    )
    surf = ax.plot_surface(
        *np.meshgrid(azimuth_sweep, elevation_sweep, indexing="ij"),
        sidelobe_levels,
        cmap=COLOR_MAPS["parula"],
        antialiased=False,
    )
    ax.set_xlabel("Azimuth [rad]")
    ax.set_ylabel("Elevation [rad]")
    ax.set_zlabel("Sidelobe level [dB]")
    ax.view_init(30, -45)
    plt.colorbar(surf)
    plt.show()

    # Plot the sidelobe level as a heatmap.
    fig, ax = plt.subplots(figsize=(12, 6))
    image = ax.imshow(
        sidelobe_levels,
        cmap=COLOR_MAPS["parula"],
        origin="lower",
        extent=(
            np.min(azimuth_sweep) - np.diff(azimuth_sweep)[0] / 2,
            np.max(azimuth_sweep) - np.diff(azimuth_sweep)[0] / 2,
            np.min(elevation_sweep) - np.diff(elevation_sweep)[0] / 2,
            np.max(elevation_sweep) - np.diff(elevation_sweep)[0] / 2,
        ),
    )
    ax.set_xlabel("Azimuth [rad]")
    ax.set_ylabel("Elevation [rad]")
    plt.colorbar(image, label="Sidelobe level [dB]")
    plt.show()


def plot_antenna_array_sidelobe_level_2d(
    array: AntennaArray,
    beam_steer: AntennaArrayBeamSteer,
) -> None:
    """Plots the sidelobe level over azimuth and elevation separately of an
    antenna array.

    Args:
        array: Antenna array.
        beam_steer: Antenna beam steering direction.
    """
    # Plot the sidelobe level over azimuth.
    azimuth_sweep = np.linspace(-np.pi / 2, np.pi / 2, 180, endpoint=False)
    azimuth_values = np.linspace(-np.pi, np.pi, 360, endpoint=False)

    azimuth_sidelobe_levels = np.zeros(azimuth_sweep.shape)
    for azimuth_index, azimuth in enumerate(azimuth_sweep):
        azimuth_beam_steer = AntennaArrayBeamSteer(
            azimuth,
            beam_steer.elevation,
        )
        radiation_pattern = array.calculate_radiation_pattern(
            azimuth_beam_steer,
            azimuth_values,
            azimuth_beam_steer.elevation,
        )
        azimuth_peak_index = np.argmin(np.abs(azimuth_values - azimuth))
        sidelobe_level = radiation_pattern.sidelobe_level(azimuth_peak_index)
        azimuth_sidelobe_levels[azimuth_index] = sidelobe_level

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(azimuth_sweep, azimuth_sidelobe_levels)
    # Plot the -3 dB threshold.
    ax.axhline(-3, color="red", linestyle="--", label=r"-3 dB threshold")
    ax.set_xlabel("Azimuth [rad]")
    ax.set_ylabel("Sidelobe level [dB]")
    ax.legend()
    plt.show()

    # Plot the sidelobe level over elevation.
    elevation_sweep = np.linspace(-np.pi / 2, np.pi / 2, 180, endpoint=False)
    elevation_values = np.linspace(-np.pi / 2, np.pi / 2, 180, endpoint=False)

    elevation_sidelobe_levels = np.zeros(elevation_sweep.shape)
    for elevation_index, elevation in enumerate(elevation_sweep):
        elevation_beam_steer = AntennaArrayBeamSteer(
            beam_steer.azimuth,
            elevation,
        )
        radiation_pattern = array.calculate_radiation_pattern(
            elevation_beam_steer,
            elevation_beam_steer.azimuth,
            elevation_values,
        )
        elevation_peak_index = np.argmin(np.abs(elevation_values - elevation))
        sidelobe_level = radiation_pattern.sidelobe_level(elevation_peak_index)
        elevation_sidelobe_levels[elevation_index] = sidelobe_level

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(elevation_sweep, elevation_sidelobe_levels)
    # Plot the -3 dB threshold.
    ax.axhline(-3, color="red", linestyle="--", label=r"-3 dB threshold")
    ax.set_xlabel("Elevation [rad]")
    ax.set_ylabel("Sidelobe level [dB]")
    ax.legend()
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

    plot_antenna_array_main_lobe_width_3d(array)
    plot_antenna_array_main_lobe_width_2d(array, beam_steer)
    plot_antenna_array_sidelobe_level_3d(array)
    plot_antenna_array_sidelobe_level_2d(array, beam_steer)


if __name__ == "__main__":
    flags.DEFINE_string(
        "config",
        "simulation/antenna/configs/ula_4_rotated_outer_recessed_patch_antenna_24ghz.pbtxt",
        "Antenna array configuration.",
    )
    flags.DEFINE_float("azimuth", 0, "Azimuth in radians.")
    flags.DEFINE_float("elevation", 0, "Elevation in radians.")

    app.run(main)
