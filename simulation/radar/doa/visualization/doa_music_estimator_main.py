"""Simulates direction-of-arrival estimation using the MUSIC algorithm and plots
the direction-of-arrival spectrum for a SIMO radar.
"""

from absl import app, flags, logging

from simulation.radar.components.adc_data import AdcData
from simulation.radar.components.radar import Radar
from simulation.radar.components.range_doppler_map import RangeDopplerMap
from simulation.radar.components.samples import Samples
from simulation.radar.components.spatial_samples import SpatialSamples
from simulation.radar.components.target import Target
from simulation.radar.doa.doa_music_estimator import DoaMusicEstimator

FLAGS = flags.FLAGS


def plot_doa_music_estimator_simo(
    rnge: float,
    range_rate: float,
    acceleration: float,
    azimuth: float,
    elevation: float,
    rcs: float,
    temperature: float,
    oversampling: int,
    noise: bool,
    num_snapshots: int,
) -> None:
    """Plots the direction-of-arrival spectrum for a SIMO radar.

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

    spatial_samples_snapshots = []
    for _ in range(num_snapshots):
        samples = Samples(adc_data)
        if noise:
            samples.add_samples(radar.generate_noise(adc_data.shape))

        range_doppler_map = RangeDopplerMap(samples, radar)
        range_doppler_map.apply_2d_window()
        range_doppler_map.perform_2d_fft()
        range_doppler_map.fft_shift()

        spatial_samples = SpatialSamples(radar, target, range_doppler_map)
        spatial_samples_snapshots.append(spatial_samples)

    # Use a direction-of-arrival MUSIC estimator to perform direction-of-arrival
    # estimation.
    doa_estimator = DoaMusicEstimator(radar, spatial_samples_snapshots)
    doa_estimator.process_spatial_samples()
    elevation_estimated, azimuth_estimated = doa_estimator.estimate_doa()
    logging.info("Estimated azimuth: %f rad, actual azimuth: %f rad.",
                 azimuth_estimated, azimuth)
    logging.info("Estimated elevation: %f radar, actual elevation: %f rad.",
                 elevation_estimated, elevation)
    doa_estimator.plot_2d_spectrum()


def main(argv):
    assert len(argv) == 1, argv
    plot_doa_music_estimator_simo(
        FLAGS.range,
        FLAGS.range_rate,
        FLAGS.acceleration,
        FLAGS.azimuth,
        FLAGS.elevation,
        FLAGS.rcs,
        FLAGS.temperature,
        FLAGS.oversampling,
        FLAGS.noise,
        FLAGS.num_snapshots,
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
    flags.DEFINE_integer("num_snapshots", 4, "Number of snapshots.")

    app.run(main)
