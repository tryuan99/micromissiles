from absl import app, flags

from utils.serial import serial_logger

FLAGS = flags.FLAGS


def main(argv):
    assert len(argv) == 1

    logger = serial_logger.SerialLogger(FLAGS.port, FLAGS.baudrate,
                                        FLAGS.output_file, FLAGS.log_to_stderr)
    logger.run()


if __name__ == "__main__":
    flags.DEFINE_string("port", "/dev/tty.SLAB_USBtoUART2",
                        "Serial port to log.")
    flags.DEFINE_integer("baudrate", 921600, "Serial port baud rate.")
    flags.DEFINE_string("output_file", None, "Output file to log the data to.")
    flags.DEFINE_boolean(
        "log_to_stderr",
        True,
        "If true, log the received data to standard error in addition to the output file.",
    )
    flags.mark_flag_as_required("output_file")

    app.run(main)
