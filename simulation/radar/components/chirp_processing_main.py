"""Performs range processing on various chirps."""

import matplotlib.pyplot as plt
import numpy as np
from absl import app, flags, logging

from simulation.radar.components.adc_data import AdcData
from simulation.radar.components.chirp import CHIRP_MAP, ChirpType
from simulation.radar.components.radar import Radar
from simulation.radar.components.samples import Samples
from simulation.radar.components.target import Target
from utils import constants

FLAGS = flags.FLAGS

ALL_CHIRPS = "all"


def process_chirp(
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
    fig, ax = plt.subplots(figsize=(12, 8))

    r_axis = np.arange(0, radar.r_max * 2, 0.01)
    chirp_types = (ChirpType.values()
                   if chirp_type == ALL_CHIRPS else [chirp_type])
    for chirp_type in chirp_types:
        output = _process_chirp_with_matched_filter(radar, targets, r_axis,
                                                    noise, chirp_type)
        output_magnitude_db = constants.mag2db(output.get_abs_samples())
        plt.plot(r_axis, output_magnitude_db, label=chirp_type.capitalize())
    ax.set_title(f"Range spectrum using a nonlinear chirp")
    ax.set_xlabel("Range in m")
    ax.set_ylabel("Magnitude in dB")
    plt.legend()
    plt.show()


def _process_chirp_with_matched_filter(
    radar: Radar,
    targets: list[Target],
    r_axis: np.ndarray,
    noise: bool,
    chirp_type: ChirpType,
) -> Samples:
    """Performs range processing on the given chirp type with a matched filter.

    Args:
        radar: Radar.
        targets: List of targets.
        r_axis: Range axis.
        noise: If true, add noise.
        chirp_type: Chirp type.

    Returns:
        Samples after range processing.
    """
    samples = np.add.reduce(
        [AdcData(radar, target, chirp_type) for target in targets])
    if noise:
        samples += radar.generate_noise(samples.shape)

    if chirp_type == ChirpType.LINEAR:
        r_max = radar.c * radar.fs / (2 * radar.mu)
        r_res = r_max / radar.N_r
        window = radar.window_r
        matched_filter = np.exp(1j * 2 * np.pi *
                                np.arange(radar.N_bins_r)[..., np.newaxis] *
                                r_axis / radar.r_max)
    elif chirp_type == ChirpType.QUADRATIC:
        r_max = radar.c * radar.fs / (2 * radar.b)
        r_res = (radar.c * radar.fs /
                 (2 * (radar.b + radar.a * radar.Tc) * radar.N_bins_r))
        n = (np.sqrt(radar.a / 2) * np.arange(radar.N_r + 2) / radar.fs +
             radar.b / np.sqrt(2 * radar.a))**2
        M = (np.sqrt(radar.a / 2) * (radar.N_r + 1) / radar.fs +
             radar.b / np.sqrt(2 * radar.a))**2
        window = (0.42 - 0.5 * np.cos(2 * np.pi * n / M) +
                  0.08 * np.cos(4 * np.pi * n / M))[1:-1]
        window /= np.linalg.norm(window)
        matched_filter = np.exp(
            1j * 2 * np.pi *
            (np.sqrt(radar.a / 2) * np.arange(radar.N_bins_r)[..., np.newaxis] /
             radar.fs + radar.b / np.sqrt(2 * radar.a))**2 *
            (2 * r_axis / radar.c))
    elif chirp_type == ChirpType.EXPONENTIAL:
        r_max = (radar.c / (2 * radar.alpha) *
                 np.log(1 / (1 - radar.fs / radar.beta)))
        r_res = (radar.c / (2 * radar.alpha) *
                 np.log(1 / (1 - radar.fs /
                             (radar.beta * radar.N_r *
                              np.exp(radar.alpha *
                                     (radar.Tc - 2 * radar.r_max / radar.c))))))
        n = np.exp(radar.alpha * np.arange(radar.N_r + 2) / radar.fs)
        M = np.exp(radar.alpha * (radar.N_r + 1) / radar.fs)
        window = (0.42 - 0.5 * np.cos(2 * np.pi * n / M) +
                  0.08 * np.cos(4 * np.pi * n / M))[1:-1]
        window /= np.linalg.norm(window)
        matched_filter = np.exp(
            1j * 2 * np.pi *
            np.exp(radar.alpha * np.arange(radar.N_bins_r)[..., np.newaxis] /
                   radar.fs) *
            (radar.beta / radar.alpha *
             (1 - np.exp(-radar.alpha * 2 * r_axis / radar.c))))
    else:
        raise ValueError(f"Unimplemented chirp type: {chirp_type}.")

    logging.info("%s chirp:", chirp_type.capitalize())
    logging.info("Maximum range: %f m.", r_max)
    logging.info("Range resolution: %f m.", r_res)

    windowed_samples = Samples(samples.samples * window[..., np.newaxis, :])
    output = Samples(
        np.squeeze(windowed_samples.samples @ np.conjugate(matched_filter)))
    output_magnitude_db = constants.mag2db(output.get_abs_samples())

    # Find the range bin with the peak.
    range_bin_index = np.argmax(output_magnitude_db)
    logging.info("Peak location at range bin %d (%f m).", range_bin_index,
                 r_axis[range_bin_index])
    return output


def main(argv):
    assert len(argv) == 1, argv
    process_chirp(
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
