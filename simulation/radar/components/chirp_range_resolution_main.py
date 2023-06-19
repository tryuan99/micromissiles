"""Simulates the range resolution of a chirp.

The simulation sweeps the phase difference between targets while plotting the
range spectrum.
"""

import matplotlib.pyplot as plt
import numpy as np
from absl import app, flags
from matplotlib import animation

from simulation.radar.components.adc_data import AdcData
from simulation.radar.components.chirp import CHIRP_MAP, ChirpType
from simulation.radar.components.radar import Radar
from simulation.radar.components.samples import Samples
from simulation.radar.components.target import Target
from utils import constants

FLAGS = flags.FLAGS

# Animation interval in milliseconds.
ANIMATION_INTERVAL = 20  # milliseconds


def plot_range_resolution(
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
    """Plots the range spectrum after range processing on the chirp.

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

    # Plot the range spectrum.
    r_axis = np.arange(np.max(rnge - 10, 0), rnge + 10, 0.01)
    theta_axis = np.linspace(0, 2 * np.pi, 360, endpoint=False)
    fig, ax = plt.subplots(figsize=(12, 8))
    line, = ax.plot(r_axis, np.log(np.zeros(r_axis.shape)))

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
        output = _process_chirp_with_matched_filter(radar, targets, frame,
                                                    r_axis, noise, chirp_type)
        output_magnitude_db = constants.mag2db(output.get_abs_samples())
        line.set_data(r_axis, output_magnitude_db)
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
    r_axis: np.ndarray,
    noise: bool,
    chirp_type: ChirpType,
) -> Samples:
    """Performs range processing on the given chirp type with a matched filter.

    Args:
        radar: Radar.
        targets: List of targets.
        theta: Phase offset between the targets.
        r_axis: Range axis.
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

    if chirp_type == ChirpType.LINEAR:
        window = radar.window_r
        matched_filter = np.exp(
            1j * 2 * np.pi * np.arange(radar.N_bins_r)[:, np.newaxis] * r_axis /
            radar.r_max)
    elif chirp_type == ChirpType.QUADRATIC:
        n = (np.sqrt(radar.a / 2) * np.arange(radar.N_r + 2) / radar.fs +
             radar.b / np.sqrt(2 * radar.a))**2
        M = (np.sqrt(radar.a / 2) * (radar.N_r + 1) / radar.fs +
             radar.b / np.sqrt(2 * radar.a))**2
        window = (0.42 - 0.5 * np.cos(2 * np.pi * n / M) +
                  0.08 * np.cos(4 * np.pi * n / M))[1:-1]
        window /= np.linalg.norm(window)
        matched_filter = np.exp(
            1j * 2 * np.pi *
            (np.sqrt(radar.a / 2) * np.arange(radar.N_bins_r)[:, np.newaxis] /
             radar.fs + radar.b / np.sqrt(2 * radar.a))**2 *
            (2 * r_axis / radar.c))
    elif chirp_type == ChirpType.EXPONENTIAL:
        n = np.exp(radar.alpha * np.arange(radar.N_r + 2) / radar.fs)
        M = np.exp(radar.alpha * (radar.N_r + 1) / radar.fs)
        window = (0.42 - 0.5 * np.cos(2 * np.pi * n / M) +
                  0.08 * np.cos(4 * np.pi * n / M))[1:-1]
        window /= np.linalg.norm(window)
        matched_filter = np.exp(
            1j * 2 * np.pi *
            np.exp(radar.alpha * np.arange(radar.N_bins_r)[:, np.newaxis] /
                   radar.fs) *
            (radar.beta / radar.alpha *
             (1 - np.exp(-radar.alpha * 2 * r_axis / radar.c))))
    else:
        raise ValueError(f"Unimplemented chirp type: {chirp_type}.")

    windowed_samples = Samples(np.einsum("kij,j->kij", samples.samples, window))
    return Samples(
        np.squeeze(windowed_samples.samples @ np.conjugate(matched_filter)))


def main(argv):
    assert len(argv) == 1, argv
    plot_range_resolution(
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
