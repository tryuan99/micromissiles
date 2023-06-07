"""Plots the instantaneous frequency of various chirps and their IF signals."""

import matplotlib.pyplot as plt
import numpy as np
from absl import app, flags

from simulation.radar.components.chirp import CHIRP_MAP, ChirpType
from simulation.radar.components.radar import Radar

FLAGS = flags.FLAGS

ALL_CHIRPS = "all"


def plot_all_chirps(rnge: float):
    """Plots the instantaneous frequency of all chirps and of their IF signals.

    Args:
        rnge: Range in m.
    """
    radar = Radar()
    tau = 2 * np.full_like(radar.t_axis_chirp, rnge) / radar.c

    # Plot the waveform of all chirps.
    fig, ax = plt.subplots(figsize=(12, 8))
    for chirp_type in CHIRP_MAP:
        chirp = CHIRP_MAP[chirp_type](radar)
        plt.plot(radar.t_axis_chirp,
                 chirp.get_signal(real=True),
                 label=chirp_type.capitalize())
    ax.set_title("Chirp waveform")
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Amplitude")
    plt.legend()
    plt.show()

    # Plot the instantaneous frequency of all chirps.
    fig, ax = plt.subplots(figsize=(12, 8))
    for chirp_type in CHIRP_MAP:
        chirp = CHIRP_MAP[chirp_type](radar)
        plt.plot(radar.t_axis_chirp,
                 chirp.get_frequency(),
                 label=chirp_type.capitalize())
    ax.set_title("Instantaneous frequency of all chirps")
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Frequency [Hz]")
    plt.legend()
    plt.show()

    # Plot the waveform of the IF of the chirp.
    fig, ax = plt.subplots(figsize=(12, 8))
    for chirp_type in CHIRP_MAP:
        chirp = CHIRP_MAP[chirp_type](radar)
        plt.plot(radar.t_axis_chirp,
                 chirp.get_if_signal(tau, real=True),
                 label=chirp_type.capitalize())
    ax.set_title("IF waveform")
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Amplitude")
    plt.legend()
    plt.show()

    # Plot the instantaneous frequency of the chirp.
    fig, ax = plt.subplots(figsize=(12, 8))
    for chirp_type in CHIRP_MAP:
        chirp = CHIRP_MAP[chirp_type](radar)
        plt.plot(radar.t_axis_chirp,
                 chirp.get_if_frequency(tau),
                 label=chirp_type.capitalize())
    ax.set_title("Instantaneous frequency of the IF")
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Frequency [Hz]")
    plt.legend()
    plt.show()


def plot_chirp(
    rnge: float,
    chirp_type: ChirpType,
) -> None:
    """Plots the instantaneous frequency of the chirp and of its IF signal.

    Args:
        rnge: Range in m.
        chirp_type: Chirp type.
    """
    radar = Radar()
    tau = 2 * np.full_like(radar.t_axis_chirp, rnge) / radar.c
    chirp = CHIRP_MAP[chirp_type](radar)

    # Plot the waveform of the chirp.
    fig, ax = plt.subplots(figsize=(12, 8))
    plt.plot(radar.t_axis_chirp, chirp.get_signal(real=True))
    ax.set_title(f"Waveform of a {chirp_type} chirp")
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Amplitude")
    plt.show()

    # Plot the instantaneous frequency of the chirp.
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.plot(radar.t_axis_chirp, chirp.get_frequency())
    ax.set_title(f"Instantaneous frequency of a {chirp_type} chirp")
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Frequency [Hz]")
    plt.show()

    # Plot the waveform of the IF of the chirp.
    fig, ax = plt.subplots(figsize=(12, 8))
    plt.plot(radar.t_axis_chirp, chirp.get_if_signal(tau, real=True))
    ax.set_title(f"IF waveform of a {chirp_type} chirp")
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Amplitude")
    plt.show()

    # Plot the instantaneous frequency of the IF of the chirp.
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.plot(radar.t_axis_chirp, chirp.get_if_frequency(tau))
    ax.set_title(f"Instantaneous frequency of the IF of a {chirp_type} chirp")
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Frequency [Hz]")
    plt.show()


def main(argv):
    assert len(argv) == 1, argv
    if FLAGS.chirp_type == ALL_CHIRPS:
        plot_all_chirps(FLAGS.range)
    else:
        plot_chirp(
            FLAGS.range,
            FLAGS.chirp_type,
        )


if __name__ == "__main__":
    flags.DEFINE_float("range", 50, "Range in m.", lower_bound=0.0)
    flags.DEFINE_enum("chirp_type", ChirpType.LINEAR,
                      ChirpType.values() + [ALL_CHIRPS], "Chirp type.")

    app.run(main)
