"""The Thorlabs motor class is an interface for a Thorlabs stepper motor.

See https://pylablib.readthedocs.io/en/latest/.apidoc/pylablib.devices.Thorlabs.html#pylablib.devices.Thorlabs.kinesis.KinesisMotor
for the API reference.
"""

from pylablib.devices import Thorlabs

from utils.devices.motor import Motor


class ThorlabsMotor(Motor):
    """Interface for a Thorlabs motor.

    Attributes:
        motor: Kinesis motor.
    """

    def __init__(self, serial_number: str, stage: str) -> None:
        self.motor = Thorlabs.KinesisMotor(serial_number, scale=stage)

    def stage(self) -> str:
        """Returns the name of the stage."""
        return self.motor.get_stage()

    def status(self) -> list[str]:
        """Returns the status of the motor."""
        return self.motor.get_status()

    def scale(self) -> tuple[float, float, float]:
        """Returns a tuple of the position scale, velocity scale, and
        acceleration scale.
        """
        return self.motor.get_scale()

    def scale_units(self) -> str:
        """Returns the units for the scaling coefficients."""
        return self.motor.get_scale_units()

    def home(self) -> None:
        """Homes the device."""
        self.motor.home()

    def is_homed(self) -> bool:
        """Returns whether the device is homed."""
        return self.motor.is_homed()

    def position(self) -> float:
        """Returns the position of the motor in degrees."""
        return self.motor.get_position()

    def move_to(self, position: float) -> None:
        """Move the motor to the desired angle.

        Args:
            position: Absolute position in degrees.
        """
        self.motor.move_to(position)
        self.motor.wait_move()

    def move_by(self, position: float) -> None:
        """Move the motor by the desired angle.

        Args:
            position: Relative position in degrees.
        """
        self.motor.move_by(position)
        self.motor.wait_move()

    def stop(self, immediate=False) -> None:
        """Stops the motion.

        Args:
            immediate: If true, stop abruptly.
        """
        self.motor.stop(immediate=immediate)

    @staticmethod
    def list_devices() -> list[tuple[str, str]]:
        """Lists all connected devices.

        Returns:
            A list of tuples consisting of the device ID and a description.
        """
        return Thorlabs.list_kinesis_devices()
