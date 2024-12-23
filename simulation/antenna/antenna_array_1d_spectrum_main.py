"""Simulates the spectrum of a linear antenna array."""

import google.protobuf
import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from absl import app, flags
from matplotlib import animation

from simulation.antenna.antenna_array import AntennaArray, AntennaArrayArrival
from simulation.antenna.antenna_array_1d_spectrum import AntennaArray1DSpectrum
from simulation.antenna.proto.antenna_array_config_pb2 import \
    AntennaArrayConfig
from utils import constants

FLAGS = flags.FLAGS

ANIMATION_INTERVAL = 20  # milliseconds


def sweep_azimuth_spectrum(array: AntennaArray) -> None:
    """Sweeps the azimuth spectrum as a function of the azimuth.

    Args:
        array: Antenna array.
    """
    spectrum = AntennaArray1DSpectrum(array)
    azimuth_sweep = np.linspace(-np.pi / 2, np.pi / 2, 180, endpoint=False)
    azimuth = np.linspace(-np.pi / 2, np.pi / 2, 360, endpoint=False)

    # Plot the spectrum in an animation.
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 6))
    line, = ax.plot(azimuth, np.zeros(len(azimuth)))

    def init_animation() -> None:
        """Initializes the animation."""
        ax.set_title("Azimuth spectrum")
        ax.set_xlabel("Azimuth in rad")
        ax.set_ylabel("Magnitude in dB")
        ax.set_ylim((-20, 20))

    def update_animation(frame: float) -> None:
        """Updates the animation for the next frame.

        Args:
            frame: Azimuth to plot.
        """
        arrival = AntennaArrayArrival(azimuth=frame)
        data = spectrum.calculate_azimuth_spectrum(arrival, azimuth)
        line.set_data(azimuth, constants.mag2db(np.abs(data)))
        ax.set_title(rf"Azimuth spectrum (azimuth = ${frame}$ rad)")

    anim = animation.FuncAnimation(
        fig,
        update_animation,
        frames=azimuth_sweep,
        init_func=init_animation,
        interval=ANIMATION_INTERVAL,
    )
    plt.show()


def sweep_azimuth_spectrum_resolution(
    array: AntennaArray,
    delta_azimuth: float,
) -> None:
    """Sweeps the azimuth spectrum as a function of the azimuth with two targets.

    Args:
        array: Antenna array.
        delta_azimuth: Difference in azimuth.
    """
    spectrum = AntennaArray1DSpectrum(array)
    azimuth_sweep = np.linspace(-np.pi / 2, np.pi / 2, 180, endpoint=False)
    azimuth = np.linspace(-np.pi / 2, np.pi / 2, 360, endpoint=False)

    # Plot the spectrum in an animation.
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 6))
    line, = ax.plot(azimuth, np.zeros(len(azimuth)))

    def init_animation() -> None:
        """Initializes the animation."""
        ax.set_title("Azimuth spectrum")
        ax.set_xlabel("Azimuth in rad")
        ax.set_ylabel("Magnitude in dB")
        ax.set_ylim((-20, 20))

    def update_animation(frame: float) -> None:
        """Updates the animation for the next frame.

        Args:
            frame: Azimuth to plot.
        """
        arrivals = [
            AntennaArrayArrival(azimuth=frame),
            AntennaArrayArrival(azimuth=frame + delta_azimuth),
        ]
        data = spectrum.calculate_azimuth_spectrum(arrivals, azimuth)
        line.set_data(azimuth, constants.mag2db(np.abs(data)))
        ax.set_title(rf"Azimuth spectrum (azimuth = ${frame}$ rad)")

    anim = animation.FuncAnimation(
        fig,
        update_animation,
        frames=azimuth_sweep,
        init_func=init_animation,
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

    sweep_azimuth_spectrum(array)
    sweep_azimuth_spectrum_resolution(array, FLAGS.delta_azimuth)


if __name__ == "__main__":
    flags.DEFINE_string("config",
                        "simulation/antenna/configs/ula_4_isotropic.pbtxt",
                        "Antenna array configuration.")
    flags.DEFINE_float("delta_azimuth", 0.2,
                       "Difference in azimuth in radians.")

    app.run(main)
