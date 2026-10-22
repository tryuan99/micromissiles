"""Sweeps the Pololu Tic motor while capturing the FieldFox output."""

import time
from pathlib import Path

from absl import app, flags, logging

from utils.devices.fieldfox_interface import FieldFoxInterface
from utils.devices.pololu_tic_motor import (PololuTicMotor,
                                            PololuTicMotorStepMode)

FLAGS = flags.FLAGS

# Number of steps per platform revolution.
# The stepper motor has a step angle of 1.8 degrees with a 180:1 transmission
# ratio.
NUM_STEPS_PER_REVOLUTION = 200 * 180

# Maximum current in A.
MAX_CURRENT = 1

# Maximum degrees per second.
MAX_DEGREES_PER_SECOND = 5

# Capture timeout in seconds.
CAPTURE_TIMEOUT = 1


def main(argv):
    assert len(argv) == 1

    motor = PololuTicMotor(
        NUM_STEPS_PER_REVOLUTION,
        PololuTicMotorStepMode.STEP_1_16,
        max_current=MAX_CURRENT,
        max_degrees_per_second=MAX_DEGREES_PER_SECOND,
    )
    logging.info("Status: %s", motor.status())
    if FLAGS.home:
        motor.home()

    output_dir_path = Path(FLAGS.output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)

    field_fox = FieldFoxInterface(FLAGS.fieldfox_ip_address)
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
    flags.DEFINE_string("fieldfox_ip_address", "192.168.1.1",
                        "FieldFox IP address.")
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
