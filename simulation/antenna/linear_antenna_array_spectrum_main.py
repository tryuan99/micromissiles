"""Simulates the spectrum of a linear antenna array."""

import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from absl import app, flags
from matplotlib import animation

from simulation.antenna.antenna_array import (AntennaArray,
                                              AntennaArrayArrival,
                                              AntennaArrayElement)
from simulation.antenna.linear_antenna_array_spectrum import \
    LinearAntennaArraySpectrum

FLAGS = flags.FLAGS

ANIMATION_INTERVAL = 20  # milliseconds


def sweep_azimuth_spectrum(num_antennas: int, antenna_spacing: float) -> None:
    """Sweeps the azimuth spectrum as a function of the azimuth.

    Args:
        num_antennas: Number of antennas.
        antenna_spacing: Antenna spacing in units of lambda.
    """
    # Create the antenna array.
    elements = [
        AntennaArrayElement(x=antenna_spacing * i) for i in range(num_antennas)
    ]
    array = AntennaArray(elements)
    spectrum = LinearAntennaArraySpectrum(array)

    azimuth = np.linspace(-np.pi / 2, np.pi / 2, 180, endpoint=False)
    theta = np.linspace(-np.pi / 2, np.pi / 2, 360, endpoint=False)

    # Plot the spectrum in an animation.
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 8))
    line, = ax.plot(theta, np.zeros(len(theta)))

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
        data = spectrum.calculate_azimuth_spectrum(arrival, theta)
        line.set_data(theta, 20 * np.log10(np.abs(data)))
        ax.set_title(f"Azimuth spectrum (theta = {frame})")

    anim = animation.FuncAnimation(
        fig,
        update_animation,
        frames=azimuth,
        init_func=init_animation,
        interval=ANIMATION_INTERVAL,
    )
    plt.show()


def sweep_azimuth_spectrum_resolution(num_antennas: int, antenna_spacing: float,
                                      delta_azimuth: float) -> None:
    """Sweeps the azimuth spectrum as a function of the azimuth with two targets.

    Args:
        num_antennas: Number of antennas.
        antenna_spacing: Antenna spacing in units of lambda.
        delta_azimuth: Difference in azimuth.
    """
    # Create the antenna array.
    elements = [
        AntennaArrayElement(x=antenna_spacing * i) for i in range(num_antennas)
    ]
    array = AntennaArray(elements)
    spectrum = LinearAntennaArraySpectrum(array)

    azimuth = np.linspace(-np.pi / 2, np.pi / 2, 180, endpoint=False)
    theta = np.linspace(-np.pi / 2, np.pi / 2, 360, endpoint=False)

    # Plot the spectrum in an animation.
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 8))
    line, = ax.plot(theta, np.zeros(len(theta)))

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
        data = spectrum.calculate_azimuth_spectrum(arrivals, theta)
        line.set_data(theta, 20 * np.log10(np.abs(data)))
        ax.set_title(f"Azimuth spectrum (theta = {frame})")

    anim = animation.FuncAnimation(
        fig,
        update_animation,
        frames=azimuth,
        init_func=init_animation,
        interval=ANIMATION_INTERVAL,
    )
    plt.show()


def main(argv):
    assert len(argv) == 1, argv

    sweep_azimuth_spectrum(FLAGS.num_antennas, FLAGS.antenna_spacing)
    sweep_azimuth_spectrum_resolution(FLAGS.num_antennas, FLAGS.antenna_spacing,
                                      FLAGS.delta_azimuth)


if __name__ == "__main__":
    flags.DEFINE_integer("num_antennas", 4, "Number of antennas.")
    flags.DEFINE_float("antenna_spacing", 0.5,
                       "Antenna spacing in units of lambda.")
    flags.DEFINE_float("delta_azimuth", 0.2,
                       "Difference in azimuth in radians.")

    app.run(main)
