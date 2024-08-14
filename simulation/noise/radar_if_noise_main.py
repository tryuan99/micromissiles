"""Plots the range spectrum with thermal and phase noise."""

import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from absl import app, flags

from simulation.noise.phase_noise import IFPhaseNoise
from simulation.radar.components.adc_data import AdcData
from simulation.radar.components.radar import Radar, Target
from simulation.radar.components.samples import Samples
from simulation.radar.processors.range_doppler_processor import \
    RangeDopplerFftProcessor
from utils import constants

FLAGS = flags.FLAGS


def plot_range_spectrum(ranges: list[float]) -> None:
    """Plots the range spectrum with thermal and phase noise.

    Args:
        ranges: List of target ranges in m.
    """
    radar = Radar()
    radar.N_tx = 1
    radar.N_rx = 1
    radar.N_v = 1

    adc_data = Samples(np.zeros(radar.N_r, dtype=np.complex128))
    for rnge in ranges:
        target = Target(rnge=rnge)
        adc_data += AdcData(radar, target)

        # Generate phase noise.
        phase_noise = IFPhaseNoise(target, radar)
        adc_data += phase_noise.generate_noise_samples(
            AdcData.get_if_amplitude(radar, target), radar.N_r)

    # Generate thermal noise.
    samples = adc_data + radar.generate_noise(adc_data.shape)

    # Perform the range FFT.
    range_doppler_map = RangeDopplerFftProcessor(samples, radar)
    range_doppler_map.apply_window_axis2()
    range_doppler_map.apply_fft_axis2()

    # Calculate the range spectrum.
    range_fft = Samples(np.squeeze(range_doppler_map.samples))
    range_fft_abs_db = constants.mag2db(range_fft.get_abs_samples())

    # Plot the range spectrum.
    plt.style.use(["science", "grid"])
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.plot(radar.r_axis, range_fft_abs_db)
    ax.set_xlabel("Range in m")
    ax.set_ylabel("Range FFT magnitude in dB")
    plt.show()


def main(argv):
    assert len(argv) == 1, argv

    plot_range_spectrum(FLAGS.range)


if __name__ == "__main__":
    flags.DEFINE_multi_integer("range",
                               10,
                               "Target range in m.",
                               lower_bound=0.0)

    app.run(main)
