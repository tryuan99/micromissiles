"""Runs the TI radar azimuth-elevation map plotter."""

from absl import app, flags

from radar.ti.ti_radar_azimuth_elevation_map_plotter import \
    TiRadarAzimuthElevationMapPlotter
from radar.ti.ti_radar_config import RADAR_CONFIGS
from radar.ti.ti_radar_data_logger import TiRadarDataLogger
from radar.ti.ti_radar_interface import (TI_CONFIG_BAUDRATE, TI_DATA_BAUDRATE,
                                         TiRadarInterface)
from radar.ti.ti_radar_subframe_data_aggregator import \
    TiRadarSubframeDataAggregator
from radar.ti.ti_radar_subframe_data_logger import TiRadarSubframeDataLogger

FLAGS = flags.FLAGS


def main(argv):
    assert len(argv) == 1, argv

    radar_config = RADAR_CONFIGS[FLAGS.board]()
    radar_interface = TiRadarInterface(FLAGS.config_port, FLAGS.data_port,
                                       FLAGS.config_baudrate,
                                       FLAGS.data_baudrate)
    radar_interface.add_config_handler(TiRadarDataLogger())
    subframe_data_aggregator = TiRadarSubframeDataAggregator()
    subframe_data_aggregator.add_subframe_data_handler(
        TiRadarSubframeDataLogger())
    plotter = TiRadarAzimuthElevationMapPlotter(radar_config, FLAGS.range,
                                                FLAGS.num_azimuth_bins,
                                                FLAGS.num_elevation_bins,
                                                FLAGS.animation_interval,
                                                FLAGS.mark_peak)
    subframe_data_aggregator.add_subframe_data_handler(plotter)
    radar_interface.add_data_handler(subframe_data_aggregator)
    radar_interface.start(radar_config)
    plotter.plot()


if __name__ == "__main__":
    flags.DEFINE_enum("board", "iwr68xx", RADAR_CONFIGS.keys(),
                      "TI radar board.")
    flags.DEFINE_string("config_port", "/dev/tty.SLAB_USBtoUART",
                        "Configuration port.")
    flags.DEFINE_integer("config_baudrate", TI_CONFIG_BAUDRATE,
                         "Configuration baud rate.")
    flags.DEFINE_string("data_port", "/dev/tty.SLAB_USBtoUART1", "Data port.")
    flags.DEFINE_integer("data_baudrate", TI_DATA_BAUDRATE, "Data baud rate.")

    flags.DEFINE_float("range", 1.7, "Expected target range in meters.")
    flags.DEFINE_integer("num_azimuth_bins", 64, "Number of azimuth bins.")
    flags.DEFINE_integer("num_elevation_bins", 64, "Number of elevation bins.")
    flags.DEFINE_float("animation_interval", 100,
                       "Animation interval in milliseconds.")
    flags.DEFINE_bool("mark_peak", True,
                      "If true, mark the peak in the azimuth-elevation map.")

    app.run(main)
