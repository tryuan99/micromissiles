"""Simulates the spectrum of a linear antenna array."""

import google.protobuf
import matplotlib.pyplot as plt
import numpy as np
from absl import app, flags
from matplotlib import animation

import utils.visualization.mpl_config
from simulation.antenna.antenna_array import AntennaArray, AntennaArrayArrival
from simulation.antenna.antenna_array_1d_spectrum import AntennaArray1DSpectrum
from simulation.antenna.proto.antenna_array_config_pb2 import \
    AntennaArrayConfig
from utils import constants

FLAGS = flags.FLAGS

# Animation interval in milliseconds.
ANIMATION_INTERVAL = 20  # milliseconds


def sweep_azimuth_spectrum(spectrum: AntennaArray1DSpectrum) -> None:
    """Sweeps the azimuth spectrum as a function of the azimuth.

    Args:
        spectrum: 1D antenna array spectrum.
    """
    azimuth_sweep = np.linspace(-np.pi / 2, np.pi / 2, 180, endpoint=False)
    azimuth = np.linspace(-np.pi / 2, np.pi / 2, 360, endpoint=False)

    # Plot the spectrum in an animation.
    fig, ax = plt.subplots(figsize=(12, 6))
    line, = ax.plot(azimuth, np.zeros(len(azimuth)))

    # Configure the axes.
    azimuth_spectrum = spectrum.calculate_azimuth_spectrum(
        AntennaArrayArrival(azimuth=0), azimuth)
    ax.set_xlabel("Azimuth in rad")
    ax.set_ylabel("Magnitude in dB")
    ax.set_ylim(-20, constants.mag2db(np.max(np.abs(azimuth_spectrum))) + 5)
    ax.set_title("Azimuth spectrum")

    def update_animation(frame: float) -> None:
        """Updates the animation for the next frame.

        Args:
            frame: Azimuth to plot.
        """
        arrival = AntennaArrayArrival(azimuth=frame)
        data = spectrum.calculate_azimuth_spectrum(arrival, azimuth)
        line.set_data(azimuth, constants.mag2db(np.abs(data)))
        ax.set_title(f"Azimuth spectrum (azimuth = {frame:.3f} rad)")

    anim = animation.FuncAnimation(
        fig,
        update_animation,
        frames=azimuth_sweep,
        interval=ANIMATION_INTERVAL,
    )
    plt.show()


def sweep_azimuth_spectrum_resolution(
    spectrum: AntennaArray1DSpectrum,
    delta_azimuth: float,
) -> None:
    """Sweeps the azimuth spectrum as a function of the azimuth with two targets.

    Args:
        spectrum: 1D antenna array spectrum.
        delta_azimuth: Difference in azimuth.
    """
    azimuth_sweep = np.linspace(-np.pi / 2, np.pi / 2, 180, endpoint=False)
    azimuth = np.linspace(-np.pi / 2, np.pi / 2, 360, endpoint=False)

    # Plot the spectrum in an animation.
    fig, ax = plt.subplots(figsize=(12, 6))
    line, = ax.plot(azimuth, np.zeros(len(azimuth)))

    # Configure the axes.
    azimuth_spectrum = spectrum.calculate_azimuth_spectrum(
        AntennaArrayArrival(azimuth=0, amplitude=2), azimuth)
    ax.set_xlabel("Azimuth in rad")
    ax.set_ylabel("Magnitude in dB")
    ax.set_ylim(-20, constants.mag2db(np.max(np.abs(azimuth_spectrum))) + 5)
    ax.set_title("Azimuth spectrum")

    def update_animation(frame: float) -> None:
        """Updates the animation for the next frame.

        Args:
            frame: Azimuth to plot.
        """
        arrivals = [
            AntennaArrayArrival(azimuth=frame),
            AntennaArrayArrival(azimuth=frame + delta_azimuth),
        ]
        azimuth_spectrum = spectrum.calculate_azimuth_spectrum(
            arrivals, azimuth)
        line.set_data(azimuth, constants.mag2db(np.abs(azimuth_spectrum)))
        ax.set_title(f"Azimuth spectrum (azimuth = {frame:.3f} rad)")

    anim = animation.FuncAnimation(
        fig,
        update_animation,
        frames=azimuth_sweep,
        interval=ANIMATION_INTERVAL,
    )
    plt.show()


def main(argv):
    assert len(argv) == 1, argv

    # Parse the antenna array configuration and create the antenna array.
    with open(FLAGS.config, "r") as antenna_array_config_file:
        antenna_array_config = google.protobuf.text_format.Parse(
            antenna_array_config_file.read(), AntennaArrayConfig())
    array = AntennaArray.create(antenna_array_config)
    spectrum = AntennaArray1DSpectrum(array)

    sweep_azimuth_spectrum(spectrum)
    sweep_azimuth_spectrum_resolution(spectrum, FLAGS.delta_azimuth)


if __name__ == "__main__":
    flags.DEFINE_string("config",
                        "simulation/antenna/configs/ula_4_isotropic.pbtxt",
                        "Antenna array configuration.")
    flags.DEFINE_float("delta_azimuth", 0.2,
                       "Difference in azimuth in radians.")

    app.run(main)
