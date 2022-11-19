"""Simulates the IF amplitude as a function of the target range."""

from absl import app, flags
import matplotlib.pyplot as plt
import numpy as np
import scipy.constants

from simulation.if_signal import IFSignal
from simulation.radar import Radar
from simulation.target import Target
from utils import constants

FLAGS = flags.FLAGS


def plot_if_amplitude_vs_range(
    rcs: float,
    temperature: float,
) -> None:
    """Plots the IF amplitude as a function of the target range.

    Args:
        rcs: Radar cross section in dBsm.
        temperature: Temperature in C.
    """
    radar = Radar()
    target = Target(rcs=rcs)

    # Calculate the thermal noise amplitude in dBm.
    thermal_noise_amplitude_db = constants.power2db(
        scipy.constants.k
        * scipy.constants.convert_temperature(temperature, "Celsius", "Kelvin")
        * radar.B
        * 1000
    )

    # Calculate the IF amplitude for each range.
    ranges = np.arange(1, int(radar.r_max + 1))
    if_amplitudes = np.zeros(len(ranges))
    for i in range(len(ranges)):
        target.range = ranges[i]
        if_amplitudes[i] = constants.mag2db(IFSignal.get_if_amplitude(radar, target))

    # Plot the IF amplitude as a function of the target range.
    fig, ax = plt.subplots(figsize=(12, 8))
    plt.plot(ranges, if_amplitudes, label="IF amplitude")
    plt.axhline(thermal_noise_amplitude_db, color="r", label="Thermal noise amplitude")
    ax.set_title("IF amplitude vs. range")
    ax.set_xlabel("Target range in m")
    ax.set_ylabel("IF amplitude in dBm")
    plt.legend()
    plt.show()


def main(argv):
    assert len(argv) == 1, argv
    plot_if_amplitude_vs_range(
        FLAGS.rcs,
        FLAGS.temperature,
    )


if __name__ == "__main__":
    flags.DEFINE_float("rcs", -10, "Radar cross section in dBsm.")
    flags.DEFINE_float("temperature", 80, "Temperature in C.")

    app.run(main)
