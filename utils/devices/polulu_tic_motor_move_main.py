"""Moves the Polulu Tic motor to the desired position."""

from absl import app, flags, logging

from utils.devices.polulu_tic_motor import (PoluluTicMotor,
                                            PoluluTicMotorStepMode)

FLAGS = flags.FLAGS

# Number of steps per platform revolution.
# The stepper motor has a step angle of 1.8 degrees with a 180:1 transmission
# ratio.
NUM_STEPS_PER_REVOLUTION = 200 * 180

# Maximum current in A.
MAX_CURRENT = 1

# Maximum degrees per second.
MAX_DEGREES_PER_SECOND = 5


def main(argv):
    assert len(argv) == 1

    motor = PoluluTicMotor(
        NUM_STEPS_PER_REVOLUTION,
        PoluluTicMotorStepMode.STEP_1,
        max_current=MAX_CURRENT,
        max_degrees_per_second=MAX_DEGREES_PER_SECOND,
    )

    logging.info("Moving motor to %f.", FLAGS.position)
    motor.move_to(FLAGS.position)
    if FLAGS.status:
        logging.info(motor.status())


if __name__ == "__main__":
    flags.DEFINE_float("position", None, "Position in degrees.")
    flags.DEFINE_boolean("status", None, "If true, print the motor status.")
    flags.mark_flag_as_required("position")

    app.run(main)
