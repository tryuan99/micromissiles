"""Sweeps the Thorlabs motor while capturing the FieldFox output."""

import time
from pathlib import Path

from absl import app, flags, logging

from utils.devices.fieldfox_interface import FieldFoxInterface
from utils.devices.thorlabs_motor import ThorlabsMotor

FLAGS = flags.FLAGS

# Capture timeout in seconds.
CAPTURE_TIMEOUT = 1


def main(argv):
    assert len(argv) == 1

    serial_number = FLAGS.serial_number
    if serial_number is None:
        devices = ThorlabsMotor.list_devices()
        if not devices:
            raise ValueError("No devices detected.")
        serial_number = devices[0][0]

    motor = ThorlabsMotor(serial_number, FLAGS.stage)
    logging.info("Stage profile: %s", motor.stage())
    logging.info("Units: %s", motor.scale_units())

    if FLAGS.home:
        motor.home()

    output_dir_path = Path(FLAGS.output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    field_fox = FieldFoxInterface()
    position = FLAGS.start
    while position <= FLAGS.stop:
        logging.info("Moving motor to %f.", position)
        motor.move_to(position)
        time.sleep(CAPTURE_TIMEOUT)

        position_str = f"{position:.6f}".rstrip("0").rstrip(".")
        output_path = output_dir_path / f"{FLAGS.output_prefix}_{position_str}deg.s2p"
        logging.info("Capturing S2P to %s.", output_path)
        field_fox.capture_sp(output_path)

        position += FLAGS.step


if __name__ == "__main__":
    flags.DEFINE_string("serial_number", None, "Motor serial number.")
    flags.DEFINE_string("stage", "PRM1-Z8", "Motor stage.")
    flags.DEFINE_float("start", None, "Start position in degrees.")
    flags.DEFINE_float("stop", None, "Stop position in degrees.")
    flags.DEFINE_float(
        "step",
        None,
        "Step position in degrees.",
        lower_bound=0.0,
    )
    flags.DEFINE_boolean("home", True, "If true, home the motor first.")
    flags.DEFINE_string("output_dir", None, "Output directory.")
    flags.DEFINE_string("output_prefix", "antenna_sweep", "Output file prefix.")
    flags.mark_flags_as_required(["start", "stop", "step", "output_dir"])

    app.run(main)
