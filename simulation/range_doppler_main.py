"""Simulates the radar datapath processing and plots the range-Doppler map."""

from absl import app, flags
import matplotlib.pyplot as plt
import numpy as np
import scipy.constants

from simulation.if_signal import IFSignal
from simulation.noise import GaussianNoise
from simulation.radar import Radar
from simulation.target import Target
from utils import constants
from utils.visualization.color_maps import COLOR_MAPS

FLAGS = flags.FLAGS


def plot_range_doppler_map(
    range: float,
    range_rate: float,
    acceleration: float,
    rcs: float,
    temperature: float,
    oversampling: int,
    noise: bool,
) -> None:
    """Plots the range-Doppler map using a 2D FFT.

    Args:
        range: Range in m.
        range_rate: Range rate in m/s.
        acceleration: Acceleration in m/s^2.
        rcs: Radar cross section in dBsm.
        temperature: Temperature in C.
        oversampling: Oversampling factor.
        noise: If true, add noise.
    """
    radar = Radar(oversampling=oversampling)
    target = Target(
        range=range, range_rate=range_rate, acceleration=acceleration, rcs=rcs
    )
    if_signal = IFSignal(radar, target)
    thermal_noise = GaussianNoise(
        if_signal.shape,
        constants.power2mag(
            scipy.constants.k
            * scipy.constants.convert_temperature(temperature, "Celsius", "Kelvin")
            * radar.B
        ),
    )

    samples = if_signal.samples
    if noise:
        samples += thermal_noise.samples
        # TODO(titan): Add phase noise.
        # TODO(titan): Add quantization noise.

    # Apply the windows.
    s_if_w = np.einsum(
        "ij,i->ij",
        np.einsum("ij,j->ij", samples, radar.wnd_r),
        radar.wnd_v,
    )

    # Perform the 2D FFT.
    s_fft = np.fft.fft2(s_if_w, (radar.N_bins_v, radar.N_bins_r))

    # Plot the range-Doppler map
    fig = plt.figure(figsize=(12, 8))
    ax = plt.axes(projection="3d")
    surf = ax.plot_surface(
        *np.meshgrid(radar.v_axis, radar.r_axis),
        constants.mag2db(np.abs(np.fft.fftshift(s_fft, axes=0))).T,
        cmap=COLOR_MAPS["parula"],
        antialiased=False,
    )
    ax.set_title("Range-Doppler map")
    ax.set_xlabel("v in m/s")
    ax.set_ylabel("d in m")
    ax.view_init(45, -45)
    plt.colorbar(surf)
    plt.show()

    # TODO(titan): Calculate the SNR.


def main(argv):
    assert len(argv) == 1, argv
    plot_range_doppler_map(
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
    flags.DEFINE_float("range_rate", 10, "Range rate in m/s.")
    flags.DEFINE_float("acceleration", 0, "Acceleration in m/s^2.")
    flags.DEFINE_float("rcs", -10, "Radar cross section in dBsm.")
    flags.DEFINE_float("temperature", 30, "Temperature in C.")
    flags.DEFINE_integer("oversampling", 1, "Oversampling factor.", lower_bound=1)
    flags.DEFINE_boolean("noise", True, "If true, add noise.")

    app.run(main)
