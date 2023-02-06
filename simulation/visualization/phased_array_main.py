"""Simulates the SNR improvement of a phased array."""

import matplotlib.pyplot as plt
import numpy as np
from absl import app, flags, logging

from simulation.components.adc_data import AdcData
from simulation.components.radar import Radar
from simulation.components.range_doppler_map import RangeDopplerMap
from simulation.components.samples import Samples
from simulation.components.target import Target
from utils import constants

FLAGS = flags.FLAGS

# Noise temperature in Celsius.
TEMPERATURE = 20  # Celsius

# Oversampling factor.
OVERSAMPLING = 4

# Guard length around the target's peak.
GUARD_LENGTH = 4


def _simulate_range_fft(radar: Radar, target: Target):
    """Simulates the range FFT for the given radar and target.

    Args:
        radar: Radar.
        target: Target.

    Returns:
        Range-Doppler map after the range FFT.
    """
    adc_data = AdcData(radar, target)
    samples = Samples(adc_data)
    samples.add_samples(radar.generate_noise(adc_data.shape, TEMPERATURE))

    range_doppler_map = RangeDopplerMap(samples, radar)
    range_doppler_map.apply_range_window()
    range_doppler_map.perform_range_fft()
    return range_doppler_map


def _calculate_snr_db(radar: Radar, target: Target) -> float:
    """Calculates the theoretical SNR in dB after the range FFT.

    Args:
        radar: Radar.
        target: Target.

    Returns:
        Theoretical SNR in dB.
    """
    signal_fft_magnitude_db = constants.mag2db(
        radar.N_tx * radar.N_rx *
        AdcData.get_if_amplitude(radar, target)) + constants.mag2db(
            radar.get_fft_processing_gain_r())
    noise_fft_magnitude_db = constants.mag2db(
        np.sqrt(radar.N_rx) *
        radar.get_noise_amplitude(TEMPERATURE)) + constants.mag2db(
            radar.get_fft_processing_gain_r(noise=True))
    snr_db = signal_fft_magnitude_db - noise_fft_magnitude_db
    logging.info("Theoretical SNR: %f - %f = %f dB", signal_fft_magnitude_db,
                 noise_fft_magnitude_db, snr_db)
    return snr_db


def _simulate_snr_db(radar: Radar, target: Target, range_fft: Samples) -> float:
    """Simulates the empirical SNR in dB after the range FFT.

    Args:
        radar: Radar.
        target: Target.
        range_fft: Range FFT samples.

    Returns:
        Empirical SNR in dB.
    """
    range_bin_index, _ = radar.get_range_doppler_bin_indices(target)
    signal_fft_magnitude_db_simulated = constants.mag2db(
        np.abs(range_fft.samples[range_bin_index]))
    range_fft_without_target = Samples(range_fft.samples)
    # Zero out the range-Doppler bins around the target's peak.
    range_fft_without_target.samples[range_bin_index - GUARD_LENGTH *
                                     OVERSAMPLING:range_bin_index +
                                     GUARD_LENGTH * OVERSAMPLING] = 0
    noise_fft_magnitude_db_simulated = constants.mag2db(
        range_fft_without_target.get_amplitude())
    snr_db_simulated = (signal_fft_magnitude_db_simulated -
                        noise_fft_magnitude_db_simulated)
    logging.info(
        "Simulated SNR: %f - %f = %f dB",
        signal_fft_magnitude_db_simulated,
        noise_fft_magnitude_db_simulated,
        snr_db_simulated,
    )
    return snr_db_simulated


def simulate_phased_array_snr(
    range: float,
    azimuth: float,
    elevation: float,
) -> None:
    """Simulates the SNR improvement of a phased array.

    Args:
        range: Range in m.
        azimuth: Azimuth in rad.
        elevation: Elevation in rad.
    """
    target = Target(range=range, azimuth=azimuth, elevation=elevation)

    # Simulate the range FFT for a SISO radar.
    siso_radar = Radar(oversampling=OVERSAMPLING)
    siso_radar.N_tx = 1
    siso_radar.N_rx = 1
    siso_range_doppler_map = _simulate_range_fft(siso_radar, target)
    siso_range_fft = Samples(np.squeeze(siso_range_doppler_map.samples)[0])
    siso_range_fft_abs_db = constants.mag2db(np.abs(siso_range_fft.samples))

    # Calculate the theoretical and empirical SNR after the FFT.
    siso_snr_db = _calculate_snr_db(siso_radar, target)
    siso_snr_db_simulated = _simulate_snr_db(siso_radar, target, siso_range_fft)

    # Simulate the range FFT for a phased array MIMO radar.
    mimo_radar = Radar(oversampling=OVERSAMPLING)
    mimo_radar.configure_phased_array(azimuth, elevation)
    mimo_range_doppler_map = _simulate_range_fft(mimo_radar, target)
    mimo_range_fft = Samples(np.sum(mimo_range_doppler_map.samples, axis=0)[0])
    mimo_range_fft_abs_db = constants.mag2db(np.abs(mimo_range_fft.samples))

    # Calculate the theoretical and empirical SNR after the FFT.
    mimo_snr_db = _calculate_snr_db(mimo_radar, target)
    mimo_snr_db_simulated = _simulate_snr_db(mimo_radar, target, mimo_range_fft)

    # Characterize the SNR improvement of a phased array MIMO radar, which
    # should be equal to 20*log10(N_tx * N_rx / sqrt(N_rx)).
    logging.info(
        "Theoretical SNR gain due to phased array MIMO: %f dB == %f dB",
        mimo_snr_db - siso_snr_db,
        constants.mag2db(mimo_radar.N_tx * mimo_radar.N_rx /
                         np.sqrt(mimo_radar.N_rx)))
    logging.info("Simulated SNR gain due to phased array MIMO: %f dB",
                 mimo_snr_db_simulated - siso_snr_db_simulated)

    # Plot the range FFT spectrum for the SISO radar and the phased array MIMO
    # radar.
    fig, ax = plt.subplots(figsize=(12, 8))
    plt.plot(siso_radar.r_axis, siso_range_fft_abs_db, label="SISO radar")
    plt.plot(mimo_radar.r_axis,
             mimo_range_fft_abs_db,
             label="Phased array MIMO radar")
    ax.set_title("Range FFT of a SISO radar vs. phased array MIMO radar")
    ax.set_xlabel("Range in m")
    ax.set_ylabel("Range FFT magnitude in dB")
    plt.legend()
    plt.show()


def main(argv):
    assert len(argv) == 1, argv
    simulate_phased_array_snr(
        FLAGS.range,
        FLAGS.azimuth,
        FLAGS.elevation,
    )


if __name__ == "__main__":
    flags.DEFINE_float("range", 20, "Range in m.")
    flags.DEFINE_float("azimuth", 0, "Azimuth in rad.")
    flags.DEFINE_float("elevation", 0, "Elevation in rad.")

    app.run(main)
