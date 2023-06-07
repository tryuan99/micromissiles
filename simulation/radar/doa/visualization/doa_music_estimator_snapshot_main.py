"""Simulates direction-of-arrival estimation using the MUSIC algorithm and plots
the standard deviation of the estimated azimuth and elevation as a function of
the number of snapshots.
"""

import matplotlib.pyplot as plt
import numpy as np
from absl import app, flags, logging

from simulation.radar.components.adc_data import AdcData
from simulation.radar.components.radar import Radar
from simulation.radar.components.range_doppler_map import RangeDopplerMap
from simulation.radar.components.samples import Samples
from simulation.radar.components.spatial_samples import SpatialSamples
from simulation.radar.components.target import Target
from simulation.radar.doa.doa_music_estimator import DoaMusicEstimator

FLAGS = flags.FLAGS

# Number of snapshots.
NUM_SNAPSHOTS = [1, 2, 5, 10, 20, 50, 100]

# Number of iterations per number of snapshots.
NUM_ITERATIONS = 100


def plot_doa_music_estimator_simo_num_snapshots(
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
    """Plots the standard deviation of the estimated azimuth and elevation as a
    function of the number of snapshots.

    Args:
        rnge: Range in m.
        range_rate: Range rate in m/s.
        acceleration: Acceleration in m/s^2.
        azimuth: Azimuth in rad.
        elevation: Elevation in rad.
        rcs: Radar cross section in dBsm.
        temperature: Temperature in Celsius.
        oversampling: Oversampling factor.
        noise: If true, add noise.
        num_snapshots: Number of snapshots.
    """
    radar = Radar(
        temperature=temperature,
        oversampling=oversampling,
    )
    radar.N_tx = 1
    target = Target(
        rnge=rnge,
        range_rate=range_rate,
        acceleration=acceleration,
        azimuth=azimuth,
        elevation=elevation,
        rcs=rcs,
    )
    adc_data = AdcData(radar, target)

    azimuth_stddev = []
    elevation_stddev = []
    for num_snapshots in NUM_SNAPSHOTS:
        azimuths = []
        elevations = []
        for _ in range(NUM_ITERATIONS):
            spatial_samples_snapshots = []
            for _ in range(num_snapshots):
                samples = Samples(adc_data)
                if noise:
                    samples.add_samples(radar.generate_noise(adc_data.shape))

                range_doppler_map = RangeDopplerMap(samples, radar)
                range_doppler_map.apply_2d_window()
                range_doppler_map.perform_2d_fft()
                range_doppler_map.fft_shift()

                spatial_samples = SpatialSamples(radar, target,
                                                 range_doppler_map)
                spatial_samples_snapshots.append(spatial_samples)

            # Use a direction-of-arrival MUSIC estimator to perform direction-of-arrival
            # estimation.
            doa_estimator = DoaMusicEstimator(radar, spatial_samples_snapshots)
            doa_estimator.process_spatial_samples()
            elevation_estimated, azimuth_estimated = doa_estimator.estimate_doa(
            )
            azimuths.append(azimuth_estimated)
            elevations.append(elevation_estimated)
        azimuth_stddev.append(np.std(azimuths))
        elevation_stddev.append(np.std(elevations))
        logging.info(
            "Number of snapshots: %d: azimuth standard deviation: %f rad, elevation standard deviation: %f rad.",
            num_snapshots, np.std(azimuths), np.std(elevations))

    # Plot the standard deviation of the estimated azimuth and elevation.
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    ax1.plot(NUM_SNAPSHOTS, azimuth_stddev)
    ax1.set_title("Azimuth standard deviation vs. number of snapshots")
    ax1.set_xlabel("Number of snapshots")
    ax1.set_ylabel("Azimuth standard deviation [rad]")
    ax2.plot(NUM_SNAPSHOTS, elevation_stddev)
    ax2.set_title("Elevation standard deviation vs. number of snapshots")
    ax2.set_xlabel("Number of snapshots")
    ax2.set_ylabel("Elevation standard deviation [rad]")
    plt.show()


def main(argv):
    assert len(argv) == 1, argv
    plot_doa_music_estimator_simo_num_snapshots(
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
