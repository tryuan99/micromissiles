"""Simulates the signal-to-noise ratio as a function of the target range."""

from absl import app, flags
import matplotlib.pyplot as plt
import numpy as np

from simulation.adc_data import AdcData
from simulation.radar import Radar
from simulation.target import Target
from utils import constants

FLAGS = flags.FLAGS

# Minimum SNR in dB for detecting the target.
MINIMUM_SNR = 15  # dB


def plot_if_amplitude_vs_range(
    rcs: float,
    temperature: float,
) -> None:
    """Plots the signal and noise amplitudes as a function of the target range.

    Args:
        rcs: Radar cross section in dBsm.
        temperature: Temperature in Celsius.
    """
    radar = Radar()
    target = Target(rcs=rcs)
    fft_processing_gain = radar.N_r * radar.N_v

    # Calculate the noise amplitude in dB before and after the 2D FFT.
    noise_amplitude_db = constants.mag2db(radar.get_noise_amplitude(temperature))
    noise_fft_magnitude_db = noise_amplitude_db + constants.mag2db(
        np.sqrt(fft_processing_gain)
    )

    # Calculate the IF amplitude and FFT peak magnitude in dB for each range.
    ranges = np.arange(1, int(radar.r_max + 1))
    if_amplitudes = np.zeros(len(ranges))
    for i, range in enumerate(ranges):
        target.range = range
        if_amplitudes[i] = constants.mag2db(AdcData.get_if_amplitude(radar, target))
    fft_peak_magnitudes = if_amplitudes + constants.mag2db(fft_processing_gain)

    # Plot the IF amplitude as a function of the target range.
    fig, ax = plt.subplots(figsize=(12, 8))
    plt.plot(ranges, if_amplitudes, label="IF amplitude")
    plt.axhline(noise_amplitude_db, color="r", label="Noise amplitude")
    ax.set_title("IF amplitude vs. range")
    ax.set_xlabel("Target range in m")
    ax.set_ylabel("IF amplitude in dB")
    plt.legend()
    plt.show()

    # Plot the FFT peak magnitude as a function of the target range.
    fig, ax = plt.subplots(figsize=(12, 8))
    plt.plot(ranges, fft_peak_magnitudes, label="FFT peak magnitude")
    plt.axhline(noise_fft_magnitude_db, color="r", label="Noise magnitude")
    plt.axhline(
        noise_fft_magnitude_db + MINIMUM_SNR,
        color="g",
        label=f"Noise magnitude + {MINIMUM_SNR} dB",
    )
    ax.set_title("FFT peak magnitude vs. range")
    ax.set_xlabel("Target range in m")
    ax.set_ylabel("FFT peak magnitude in dB")
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
    flags.DEFINE_float("temperature", 30, "Temperature in Celsius.")

    app.run(main)
