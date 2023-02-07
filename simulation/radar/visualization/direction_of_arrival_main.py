"""Simulates the radar datapath processing and plots the range-Doppler map and
direction-of-arrival spectrum for a SIMO radar.
"""

import matplotlib.pyplot as plt
import numpy as np
from absl import app, flags

from simulation.radar.components.adc_data import AdcData
from simulation.radar.components.azimuth_elevation_map import \
    AzimuthElevationMap
from simulation.radar.components.radar import Radar
from simulation.radar.components.range_doppler_map import RangeDopplerMap
from simulation.radar.components.samples import Samples
from simulation.radar.components.target import Target
from utils import constants
from utils.visualization.color_maps import COLOR_MAPS

FLAGS = flags.FLAGS


def plot_direction_of_arrival_simo(
    rnge: float,
    range_rate: float,
    acceleration: float,
    azimuth: float,
    elevation: float,
    rcs: float,
    temperature: float,
    oversampling: int,
    noise: bool,
) -> None:
    """Plots the range-Doppler map and direction-of-arrival spectrum for a SIMO radar.

    Args:
        range: Range in m.
        range_rate: Range rate in m/s.
        acceleration: Acceleration in m/s^2.
        azimuth: Azimuth in rad.
        elevation: Elevation in rad.
        rcs: Radar cross section in dBsm.
        temperature: Temperature in Celsius.
        oversampling: Oversampling factor.
        noise: If true, add noise.
    """
    radar = Radar(temperature=temperature, oversampling=oversampling)
    radar.N_tx = 1
    target = Target(
        range=rnge,
        range_rate=range_rate,
        acceleration=acceleration,
        azimuth=azimuth,
        elevation=elevation,
        rcs=rcs,
    )
    adc_data = AdcData(radar, target)

    samples = Samples(adc_data)
    if noise:
        samples.add_samples(radar.generate_noise(adc_data.shape))

    range_doppler_map = RangeDopplerMap(samples, radar)
    range_doppler_map.apply_2d_window()
    range_doppler_map.perform_2d_fft()
    range_doppler_map.fft_shift()

    # Plot the range-Doppler map.
    fig = plt.figure(figsize=(12, 8))
    ax = plt.axes(projection="3d")
    surf = ax.plot_surface(
        *np.meshgrid(radar.v_axis, radar.r_axis),
        range_doppler_map.accumulate_log_magnitude().T,
        cmap=COLOR_MAPS["parula"],
        antialiased=False,
    )
    ax.set_title("Range-Doppler map")
    ax.set_xlabel("v in m/s")
    ax.set_ylabel("d in m")
    ax.view_init(45, -45)
    plt.colorbar(surf)
    plt.show()

    # Perform the 2D azimuth-elevation FFT.
    azimuth_elevation_map = AzimuthElevationMap(range_doppler_map, radar,
                                                target)
    azimuth_elevation_map.perform_2d_fft()
    azimuth_elevation_map.fft_shift()

    # Plot the azimuth-elevation FFT spectrum.
    fig = plt.figure(figsize=(12, 8))
    ax = plt.axes(projection="3d")
    surf = ax.plot_surface(
        *np.meshgrid(radar.el_axis, radar.az_axis),
        constants.mag2db(azimuth_elevation_map.get_abs_samples()).T,
        cmap=COLOR_MAPS["parula"],
        antialiased=False,
    )
    ax.set_title("Azimuth-elevation FFT spectrum")
    ax.set_xlabel("Elevation in rad")
    ax.set_ylabel("Azimuth in rad")
    ax.view_init(45, -45)
    plt.colorbar(surf)
    plt.show()


def main(argv):
    assert len(argv) == 1, argv
    plot_direction_of_arrival_simo(
        FLAGS.range,
        FLAGS.range_rate,
        FLAGS.acceleration,
        FLAGS.azimuth,
        FLAGS.elevation,
        FLAGS.rcs,
        FLAGS.temperature,
        FLAGS.oversampling,
        FLAGS.noise,
    )


if __name__ == "__main__":
    flags.DEFINE_float("range", 50, "Range in m.", lower_bound=0.0)
    flags.DEFINE_float("range_rate", 0, "Range rate in m/s.")
    flags.DEFINE_float("acceleration", 0, "Acceleration in m/s^2.")
    flags.DEFINE_float("azimuth", 0, "Azimuth in rad.")
    flags.DEFINE_float("elevation", 0, "Elevation in rad.")
    flags.DEFINE_float("rcs", -10, "Radar cross section in dBsm.")
    flags.DEFINE_float("temperature", 30, "Temperature in Celsius.")
    flags.DEFINE_integer("oversampling",
                         1,
                         "Oversampling factor.",
                         lower_bound=1)
    flags.DEFINE_boolean("noise", True, "If true, add noise.")

    app.run(main)
