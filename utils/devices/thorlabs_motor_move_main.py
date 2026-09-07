"""Moves the Thorlabs motor to the desired position."""

from absl import app, flags, logging

from utils.devices.thorlabs_motor import ThorlabsMotor

FLAGS = flags.FLAGS


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
    logging.info("Moving motor to %f.", FLAGS.position)
    motor.move_to(FLAGS.position)


if __name__ == "__main__":
    flags.DEFINE_string("serial_number", None, "Motor serial number.")
    flags.DEFINE_string("stage", "PRM1-Z8", "Motor stage.")
    flags.DEFINE_float("position", None, "Position in degrees.")
    flags.DEFINE_boolean("home", False, "If true, home the motor first.")
    flags.mark_flag_as_required("position")

    app.run(main)
