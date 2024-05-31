"""Runs the TI radar interface."""

from absl import app, flags

from radar.ti.ti_radar_config import RADAR_CONFIGS
from radar.ti.ti_radar_interface import (TI_CONFIG_BAUDRATE, TI_DATA_BAUDRATE,
                                         TiRadarInterface)

FLAGS = flags.FLAGS


def main(argv):
    assert len(argv) == 1, argv

    radar_interface = TiRadarInterface(FLAGS.config_port, FLAGS.data_port,
                                       FLAGS.config_baudrate,
                                       FLAGS.data_baudrate)
    radar_interface.start(RADAR_CONFIGS[FLAGS.board]())


if __name__ == "__main__":
    flags.DEFINE_enum("board", "iwr68xx", RADAR_CONFIGS.keys(),
                      "TI radar board.")
    flags.DEFINE_string("config_port", "/dev/tty.SLAB_USBtoUART",
                        "Configuration port.")
    flags.DEFINE_integer("config_baudrate", TI_CONFIG_BAUDRATE,
                         "Configuration baud rate.")
    flags.DEFINE_string("data_port", "/dev/tty.SLAB_USBtoUART2", "Data port.")
    flags.DEFINE_integer("data_baudrate", TI_DATA_BAUDRATE, "Data baud rate.")

    app.run(main)
