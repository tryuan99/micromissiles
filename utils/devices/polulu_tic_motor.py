"""The Polulu Tic motor class is an interface for a Polulu Tic stepper motor.

See https://www.pololu.com/docs/0J71/12 for the API reference.
"""

import subprocess
from enum import IntEnum

import yaml
from absl import logging

from utils.devices.motor import Motor


class PoluluTicMotorStepMode(IntEnum):
    """Polulu Tic motor step mode enumeration."""
    STEP_1 = 1
    STEP_1_2 = 2
    STEP_1_4 = 4
    STEP_1_8 = 8
    STEP_1_16 = 16
    STEP_1_32 = 32
    STEP_1_64 = 64
    STEP_1_128 = 128
    STEP_1_256 = 256


class PoluluTicMotor(Motor):
    """Interface for a Polulu Tic motor.

    Attributes:
        num_steps_per_revolution: Number of steps per revolution.
        step_mode: Step mode.
    """

    def __init__(self, num_steps_per_revolution: int,
                 step_mode: PoluluTicMotorStepMode) -> None:
        self.num_steps_per_revolution = num_steps_per_revolution
        self.step_mode = step_mode
        self.send_command(["--step-mode", str(step_mode)])

    def status(self) -> list[str]:
        """Returns the status of the motor."""
        return self.send_command(["--status"])

    def home(self) -> None:
        """Homes the device."""
        self.send_command(["--home", "fwd"])

    def position(self) -> float:
        """Returns the position of the motor in degrees."""
        status = yaml.safe_load(self.status())
        return self._microstep_to_position(status["Current position"])

    def move_to(self, position: float) -> None:
        """Move the motor to the desired angle.

        Args:
            position: Absolute position in degrees.
        """
        self.send_command(
            ["--position",
             str(self._position_to_microsteps(position))])

    def move_by(self, position: float) -> None:
        """Move the motor by the desired angle.

        Args:
            position: Relative position in degrees.
        """
        self.motor.move_by(self.position() + position)

    def stop(self) -> None:
        """Stops the motion."""
        self.send_command(["--halt-and-hold"])

    @staticmethod
    def list_devices() -> list[tuple[str, str]]:
        """Lists all connected devices.

        Returns:
            A list of tuples consisting of the device ID and a description.
        """
        return PoluluTicMotor.send_command(["--list"])

    @staticmethod
    def send_command(*args: str | list[str]) -> str:
        try:
            result = subprocess.run(
                ["ticcmd", "--exit-safe-start", *args],
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            logging.error(
                "ticcmd failed with exit code %d: %s",
                e.returncode,
                e.stderr.strip(),
            )
            raise
        return result.stdout.strip()

    def _microstep_to_position(self, value: int) -> float:
        """Converts from units of microsteps to units of degrees.

        Args:
            value: Value in microsteps.
        """
        return value * 360 / (self.num_steps_per_revolution * self.step_mode)

    def _position_to_microsteps(self, value: int) -> float:
        """Converts from units of degrees to units of microsteps.

        Args:
            value: Value in degrees.
        """
        return value * self.num_steps_per_revolution * self.step_mode / 360
