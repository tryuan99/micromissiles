"""Runs the TI radar range-Doppler map plotter."""

from absl import app, flags

from radar.ti.ti_radar_config import RADAR_CONFIGS
from radar.ti.ti_radar_data_logger import TiRadarDataLogger
from radar.ti.ti_radar_interface import (TI_CONFIG_BAUDRATE, TI_DATA_BAUDRATE,
                                         TiRadarInterface)
from radar.ti.ti_radar_range_doppler_map_plotter import \
    TiRadarRangeDopplerMapPlotter
from radar.ti.ti_radar_subframe_data_aggregator import \
    TiRadarSubframeDataAggregator
from radar.ti.ti_radar_subframe_data_logger import TiRadarSubframeDataLogger

FLAGS = flags.FLAGS


def main(argv):
    assert len(argv) == 1, argv

    radar_interface = TiRadarInterface(FLAGS.config_port, FLAGS.data_port,
                                       FLAGS.config_baudrate,
                                       FLAGS.data_baudrate)
    radar_interface.add_config_handler(TiRadarDataLogger())
    subframe_data_aggregator = TiRadarSubframeDataAggregator()
    subframe_data_aggregator.add_subframe_data_handler(
        TiRadarSubframeDataLogger())
    plotter = TiRadarRangeDopplerMapPlotter(FLAGS.num_range_bins,
                                            FLAGS.num_doppler_bins,
                                            FLAGS.animation_interval,
                                            FLAGS.mark_detections)
    subframe_data_aggregator.add_subframe_data_handler(plotter)
    radar_interface.add_data_handler(subframe_data_aggregator)
    radar_interface.start(RADAR_CONFIGS[FLAGS.board]())
    plotter.plot()


if __name__ == "__main__":
    flags.DEFINE_enum("board", "iwr68xx", RADAR_CONFIGS.keys(),
                      "TI radar board.")
    flags.DEFINE_string("config_port", "/dev/tty.SLAB_USBtoUART",
                        "Configuration port.")
    flags.DEFINE_integer("config_baudrate", TI_CONFIG_BAUDRATE,
                         "Configuration baud rate.")
    flags.DEFINE_string("data_port", "/dev/tty.SLAB_USBtoUART2", "Data port.")
    flags.DEFINE_integer("data_baudrate", TI_DATA_BAUDRATE, "Data baud rate.")

    flags.DEFINE_integer("num_range_bins", 512, "Number of range bins.")
    flags.DEFINE_integer("num_doppler_bins", 16, "Number of Doppler bins.")
    flags.DEFINE_float("animation_interval", 100,
                       "Animation interval in milliseconds.")
    flags.DEFINE_bool("mark_detections", True,
                      "If true, mark the detections in the range-Doppler map.")

    app.run(main)
