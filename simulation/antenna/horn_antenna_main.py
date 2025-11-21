"""Plots the radiation pattern of a horn antenna."""

import matplotlib.colors
import matplotlib.pyplot as plt
import numpy as np
from absl import app, flags
from matplotlib import cm

import utils.visualization.mpl_config
from simulation.antenna.horn_antenna import HornAntenna
from utils.coordinates import SphericalCoordinates
from utils.visualization.color_maps import COLOR_MAPS

FLAGS = flags.FLAGS


def plot_radiation_pattern_3d(
    a: float,
    b: float,
    a1: float,
    b1: float,
    rho1: float,
    rho2: float,
) -> None:
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
    azimuth_mesh, elevation_mesh = np.meshgrid(
        azimuth,
        elevation,
        indexing="ij",
    )

    horn_antenna = HornAntenna(a, b, a1, b1, rho1, rho2)
    radiation_pattern = horn_antenna.calculate_radiation_pattern(
        azimuth_mesh,
        elevation_mesh,
    )

    # Convert from spherical coordinates to Cartesian coordinates.
    r = radiation_pattern.db()
    x, y, z = SphericalCoordinates.transform_to_cartesian_arrays(
        range=r,
        azimuth=azimuth_mesh,
        elevation=elevation_mesh,
    )

    # Generate the face colors.
    norm = matplotlib.colors.Normalize(vmin=np.min(r), vmax=np.max(r))
    m = cm.ScalarMappable(cmap=COLOR_MAPS["parula"], norm=norm)
    m.set_array([])

    # Plot the radiation pattern.
    fig, ax = plt.subplots(
        figsize=(12, 6),
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


def plot_radiation_pattern_2d(
    a: float,
    b: float,
    a1: float,
    b1: float,
    rho1: float,
    rho2: float,
) -> None:
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
    radiation_pattern = horn_antenna.calculate_radiation_pattern(
        azimuth=azimuth,
        elevation=0,
    )
    fig, ax = plt.subplots(
        figsize=(12, 6),
        subplot_kw={"projection": "polar"},
    )
    ax.plot(azimuth, radiation_pattern.db())
    ax.set_xlabel("Azimuth")
    plt.show()

    # Plot the radiation pattern along zero azimuth.
    elevation = np.linspace(-np.pi / 2, np.pi / 2, 360, endpoint=False)
    radiation_pattern = horn_antenna.calculate_radiation_pattern(
        azimuth=0,
        elevation=elevation,
    )
    fig, ax = plt.subplots(
        figsize=(12, 6),
        subplot_kw={"projection": "polar"},
    )
    ax.plot(elevation, radiation_pattern.db())
    ax.set_xlabel("Elevation")
    plt.show()


def main(argv):
    assert len(argv) == 1, argv

    plot_radiation_pattern_3d(
        FLAGS.a,
        FLAGS.b,
        FLAGS.a1,
        FLAGS.b1,
        FLAGS.rho1,
        FLAGS.rho2,
    )
    plot_radiation_pattern_2d(
        FLAGS.a,
        FLAGS.b,
        FLAGS.a1,
        FLAGS.b1,
        FLAGS.rho1,
        FLAGS.rho2,
    )


if __name__ == "__main__":
    flags.DEFINE_float("a",
                       0.5,
                       "Width in units of lambda before the flare.",
                       lower_bound=0.0)
    flags.DEFINE_float("b",
                       0.25,
                       "Height in units of lambda before the flare.",
                       lower_bound=0.0)
    flags.DEFINE_float("a1",
                       5.5,
                       "Width in units of lambda after the flare.",
                       lower_bound=0.0)
    flags.DEFINE_float("b1",
                       2.75,
                       "Height in units of lambda after the flare.",
                       lower_bound=0.0)
    flags.DEFINE_float(
        "rho1",
        6,
        "Depth of the pyramid in the y-z plane in units of lambda.",
        lower_bound=0.0)
    flags.DEFINE_float(
        "rho2",
        6,
        "Depth of the pyramid in the x-z plane in units of lambda.",
        lower_bound=0.0)

    app.run(main)
