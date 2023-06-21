"""Simulates the range resolution of a chirp after processing using a matched
filter.

The simulation sweeps the phase difference between targets while plotting the
range spectrum.
"""

import matplotlib.pyplot as plt
import numpy as np
from absl import app, flags
from matplotlib import animation

from simulation.radar.components.adc_data import AdcData
from simulation.radar.components.chirp import ChirpType
from simulation.radar.components.radar import Radar
from simulation.radar.components.samples import Samples
from simulation.radar.components.target import Target
from simulation.radar.processors.chirp_processor import (
    ChirpMatchedFilterProcessor, ChirpMatchedFilterProcessorFactory)
from utils import constants

FLAGS = flags.FLAGS

# Animation interval in milliseconds.
ANIMATION_INTERVAL = 20  # milliseconds


def plot_range_resolution_with_matched_filter(
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
    """Plots the range spectrum after range processing using a matched filter.

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
    radar.r_axis = np.arange(np.max(rnge - 10, 0), rnge + 10, 0.01)
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

    # Plot the range spectrum.
    theta_axis = np.linspace(0, 2 * np.pi, 360, endpoint=False)
    fig, ax = plt.subplots(figsize=(12, 8))
    line, = ax.plot(radar.r_axis, np.log(np.zeros(radar.r_axis.shape)))

    def init_animation() -> None:
        """Initializes the animation."""
        ax.set_title("Range spectrum using a nonlinear chirp")
        ax.set_xlabel("Range in m")
        ax.set_ylabel("Magnitude in dB")
        ax.set_xlim((np.max(rnge - 10, 0), rnge + 10))
        ax.set_ylim((-300, -100))

    def update_animation(frame: float) -> None:
        """Updates the animation for the next frame.

        Args:
            frame: Phase offet to plot.
        """
        chirp_processor = _process_chirp_with_matched_filter(
            radar, targets, frame, noise, chirp_type)
        output_magnitude_db = constants.mag2db(
            chirp_processor.get_abs_samples())
        line.set_data(chirp_processor.get_output_axis(), output_magnitude_db)
        ax.set_title(
            f"Range spectrum using a {chirp_type} chirp (theta = {frame})")

    anim = animation.FuncAnimation(
        fig,
        update_animation,
        frames=theta_axis,
        init_func=init_animation,
        interval=ANIMATION_INTERVAL,
    )
    plt.show()


def _process_chirp_with_matched_filter(
    radar: Radar,
    targets: list[Target],
    theta: float,
    noise: bool,
    chirp_type: ChirpType,
) -> ChirpMatchedFilterProcessor:
    """Performs range processing on the given chirp type with a matched filter.

    Args:
        radar: Radar.
        targets: List of targets.
        theta: Phase offset between the targets.
        noise: If true, add noise.
        chirp_type: Chirp type.

    Returns:
        Samples after range processing.
    """
    samples = np.add.reduce([
        AdcData(radar, target, chirp_type) * np.exp(1j * theta * i)
        for i, target in enumerate(targets)
    ])
    if noise:
        samples += radar.generate_noise(samples.shape)

    chirp_processor = ChirpMatchedFilterProcessorFactory.create(
        chirp_type, samples, radar)
    chirp_processor.apply_window()
    chirp_processor.process_samples()
    return chirp_processor


def main(argv):
    assert len(argv) == 1, argv
    plot_range_resolution_with_matched_filter(
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
    flags.DEFINE_float("delta_r", 0.2, "Range difference in m.")
    flags.DEFINE_float("range_rate", 0, "Range rate in m/s.")
    flags.DEFINE_float("acceleration", 0, "Acceleration in m/s^2.")
    flags.DEFINE_float("rcs", -10, "Radar cross section in dBsm.")
    flags.DEFINE_float("temperature", 30, "Temperature in Celsius.")
    flags.DEFINE_integer("oversampling",
                         1,
                         "Oversampling factor.",
                         lower_bound=1)
    flags.DEFINE_boolean("noise", False, "If true, add noise.")
    flags.DEFINE_enum("chirp_type", ChirpType.LINEAR, ChirpType.values(),
                      "Chirp type.")

    app.run(main)
