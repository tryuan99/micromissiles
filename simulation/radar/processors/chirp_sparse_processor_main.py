"""Performs range processing on various chirps using a sparse processor."""

import matplotlib.pyplot as plt
import numpy as np
from absl import app, flags, logging

from simulation.radar.components.adc_data import AdcData
from simulation.radar.components.chirp import ChirpType
from simulation.radar.components.radar import Radar
from simulation.radar.components.samples import Samples
from simulation.radar.components.target import Target
from simulation.radar.processors.chirp_processor import (
    SparseChirpProcessor, SparseChirpProcessorFactory)
from utils import constants

FLAGS = flags.FLAGS

ALL_CHIRPS = "all"


def process_sparse_chirp(
    rnge: float,
    delta_r: float,
    range_rate: float,
    acceleration: float,
    rcs: float,
    temperature: float,
    oversampling: int,
    noise: bool,
    chirp_type: ChirpType,
) -> None:
    """Performs range processing on the chirp.

    Args:
        rnge: Range in m.
        delta_r: Range difference between targets.
        range_rate: Range rate in m/s.
        acceleration: Acceleration in m/s^2.
        rcs: Radar cross section in dBsm.
        temperature: Temperature in Celsius.
        oversampling: Oversampling factor.
        noise: If true, add noise.
        chirp_type: Chirp type.
    """
    radar = Radar(
        temperature=temperature,
        oversampling=oversampling,
    )
    radar.N_tx = 1
    radar.N_rx = 1
    radar.N_v = 1
    radar.N_bins_v = 1
    radar.r_axis = np.arange(0, radar.r_max, 0.1)
    targets = [
        Target(
            rnge=rnge,
            range_rate=range_rate,
            acceleration=acceleration,
            rcs=rcs,
        ),
        Target(
            rnge=rnge + delta_r,
            range_rate=range_rate,
            acceleration=acceleration,
            rcs=rcs,
        )
    ]

    # Plot the range spectrum for each chirp type.
    fig, ax = plt.subplots(figsize=(8, 6))
    chirp_types = (ChirpType.values()
                   if chirp_type == ALL_CHIRPS else [chirp_type])
    for chirp_type in chirp_types:
        chirp_processor = _process_sparse_chirp(radar, targets, noise,
                                                chirp_type)
        output_magnitude_db = constants.mag2db(
            chirp_processor.get_abs_samples())
        plt.scatter(chirp_processor.get_output_axis(),
                    output_magnitude_db,
                    label=chirp_type.capitalize())
    ax.set_title("Range spectrum of a nonlinear chirp with sparse processing")
    ax.set_xlabel("Range in m")
    ax.set_ylabel("Magnitude in dB")
    ax.set_xlim((np.min(radar.r_axis), np.max(radar.r_axis)))
    plt.legend()
    plt.show()


def _process_sparse_chirp(
    radar: Radar,
    targets: list[Target],
    noise: bool,
    chirp_type: ChirpType,
) -> SparseChirpProcessor:
    """Performs range processing on the given chirp type using a sparse chirp
    processor.

    Args:
        radar: Radar.
        targets: List of targets.
        noise: If true, add noise.
        chirp_type: Chirp type.

    Returns:
        Samples after range processing.
    """
    samples = np.add.reduce(
        [AdcData(radar, target, chirp_type) for target in targets])
    if noise:
        samples += radar.generate_noise(samples.shape)

    chirp_processor = SparseChirpProcessorFactory.create(
        chirp_type, samples, radar)
    chirp_processor.apply_window()
    chirp_processor.process_samples()

    logging.info("%s chirp:", chirp_type.capitalize())
    logging.info("Maximum range: %f m.", chirp_processor.r_max)
    logging.info("Range resolution: %f m.", chirp_processor.r_res)

    # Estimate the range of the peak.
    range_estimated = chirp_processor.estimate_peak()
    logging.info("Peak location at range: %f m.", range_estimated)
    return chirp_processor


def main(argv):
    assert len(argv) == 1, argv
    process_sparse_chirp(
        FLAGS.range,
        FLAGS.delta_r,
        FLAGS.range_rate,
        FLAGS.acceleration,
        FLAGS.rcs,
        FLAGS.temperature,
        FLAGS.oversampling,
        FLAGS.noise,
        FLAGS.chirp_type,
    )


if __name__ == "__main__":
    flags.DEFINE_float("range", 20, "Range in m.", lower_bound=0.0)
    flags.DEFINE_float("delta_r", 0, "Range difference in m.")
    flags.DEFINE_float("range_rate", 0, "Range rate in m/s.")
    flags.DEFINE_float("acceleration", 0, "Acceleration in m/s^2.")
    flags.DEFINE_float("rcs", -10, "Radar cross section in dBsm.")
    flags.DEFINE_float("temperature", 30, "Temperature in Celsius.")
    flags.DEFINE_integer("oversampling",
                         1,
                         "Oversampling factor.",
                         lower_bound=1)
    flags.DEFINE_boolean("noise", False, "If true, add noise.")
    flags.DEFINE_enum("chirp_type", ChirpType.LINEAR,
                      ChirpType.values() + [ALL_CHIRPS], "Chirp type.")

    app.run(main)
