"""Simulates the radar datapath processing and plots the range-Doppler map for a SISO radar."""

import matplotlib.pyplot as plt
import numpy as np
from absl import app, flags, logging

from simulation.radar.components.adc_data import AdcData
from simulation.radar.components.radar import Radar
from simulation.radar.components.range_doppler_map import RangeDopplerMap
from simulation.radar.components.samples import Samples
from simulation.radar.components.target import Target
from utils import constants
from utils.visualization.color_maps import COLOR_MAPS

FLAGS = flags.FLAGS

# Guard length around the target's peak.
GUARD_LENGTH = 1


def plot_range_doppler_map_siso(
    range: float,
    range_rate: float,
    acceleration: float,
    rcs: float,
    temperature: float,
    oversampling: int,
    noise: bool,
) -> None:
    """Plots the range-Doppler map using a 2D FFT for a SISO radar.

    Args:
        range: Range in m.
        range_rate: Range rate in m/s.
        acceleration: Acceleration in m/s^2.
        rcs: Radar cross section in dBsm.
        temperature: Temperature in Celsius.
        oversampling: Oversampling factor.
        noise: If true, add noise.
    """
    radar = Radar(temperature=temperature, oversampling=oversampling)
    radar.N_tx = 1
    radar.N_rx = 1
    target = Target(range=range,
                    range_rate=range_rate,
                    acceleration=acceleration,
                    rcs=rcs)
    adc_data = AdcData(radar, target)

    samples = Samples(adc_data)
    noise_samples = Samples(np.zeros(samples.shape))
    if noise:
        noise_samples.add_samples(radar.generate_noise(noise_samples.shape))
    samples.add_samples(noise_samples)

    range_doppler_map = RangeDopplerMap(samples, radar)
    range_doppler_map.apply_2d_window()
    range_doppler_map.perform_2d_fft()
    range_doppler_map.fft_shift()
    range_doppler_map_abs_db = constants.mag2db(
        np.squeeze(range_doppler_map.get_abs_samples()))

    # Plot the range-Doppler map.
    fig = plt.figure(figsize=(12, 8))
    ax = plt.axes(projection="3d")
    surf = ax.plot_surface(
        *np.meshgrid(radar.v_axis, radar.r_axis),
        range_doppler_map_abs_db.T,
        cmap=COLOR_MAPS["parula"],
        antialiased=False,
    )
    ax.set_title("Range-Doppler map")
    ax.set_xlabel("v in m/s")
    ax.set_ylabel("d in m")
    ax.view_init(45, -45)
    plt.colorbar(surf)
    plt.show()

    # Calculate the theoretical SNR.
    signal_amplitude_db = constants.mag2db(adc_data.get_amplitude())
    signal_fft_magnitude_db = signal_amplitude_db + constants.mag2db(
        radar.get_fft_processing_gain())
    noise_amplitude_db = constants.mag2db(noise_samples.get_amplitude())
    noise_fft_magnitude_db = noise_amplitude_db + constants.mag2db(
        radar.get_fft_processing_gain(noise=True))
    logging.info(
        "Theoretical SNR: %f - %f = %f dB",
        signal_fft_magnitude_db,
        noise_fft_magnitude_db,
        signal_fft_magnitude_db - noise_fft_magnitude_db,
    )

    # Calculate the empirical SNR.
    range_bin_index, doppler_bin_index = radar.get_range_doppler_bin_indices(
        target)
    signal_fft_magnitude_db_simulated = range_doppler_map_abs_db[
        doppler_bin_index, range_bin_index]
    range_doppler_map_without_target = Samples(range_doppler_map)
    # Zero out the range-Doppler bins around the target's peak.
    range_doppler_map_without_target.samples[:, doppler_bin_index -
                                             GUARD_LENGTH:doppler_bin_index +
                                             GUARD_LENGTH, range_bin_index -
                                             GUARD_LENGTH:range_bin_index +
                                             GUARD_LENGTH,] = 0
    noise_fft_magnitude_db_simulated = constants.mag2db(
        range_doppler_map_without_target.get_amplitude())
    logging.info(
        "Simulated SNR: %f - %f = %f dB",
        signal_fft_magnitude_db_simulated,
        noise_fft_magnitude_db_simulated,
        signal_fft_magnitude_db_simulated - noise_fft_magnitude_db_simulated,
    )


def main(argv):
    assert len(argv) == 1, argv
    plot_range_doppler_map_siso(
        FLAGS.range,
        FLAGS.range_rate,
        FLAGS.acceleration,
        FLAGS.rcs,
        FLAGS.temperature,
        FLAGS.oversampling,
        FLAGS.noise,
    )


if __name__ == "__main__":
    flags.DEFINE_float("range", 50, "Range in m.", lower_bound=0.0)
    flags.DEFINE_float("range_rate", 0, "Range rate in m/s.")
    flags.DEFINE_float("acceleration", 0, "Acceleration in m/s^2.")
    flags.DEFINE_float("rcs", -10, "Radar cross section in dBsm.")
    flags.DEFINE_float("temperature", 30, "Temperature in Celsius.")
    flags.DEFINE_integer("oversampling",
                         1,
                         "Oversampling factor.",
                         lower_bound=1)
    flags.DEFINE_boolean("noise", True, "If true, add noise.")

    app.run(main)
