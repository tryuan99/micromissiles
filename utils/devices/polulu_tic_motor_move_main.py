"""Moves the Polulu Tic motor to the desired position."""

from absl import app, flags, logging

from utils.devices.polulu_tic_motor import (PoluluTicMotor,
                                            PoluluTicMotorStepMode)

FLAGS = flags.FLAGS

# Number of steps per revolution.
NUM_STEPS_PER_REVOLUTION = 200


def main(argv):
    assert len(argv) == 1

    motor = PoluluTicMotor(
        NUM_STEPS_PER_REVOLUTION,
        PoluluTicMotorStepMode.STEP_1,
    )

    if FLAGS.home:
        motor.home()
    logging.info("Moving motor to %f.", FLAGS.position)
    motor.move_to(FLAGS.position)


if __name__ == "__main__":
    flags.DEFINE_float("position", None, "Position in degrees.")
    flags.DEFINE_boolean("home", False, "If true, home the motor first.")
    flags.mark_flag_as_required("position")

    app.run(main)
