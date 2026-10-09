"""The Polulu Tic motor class is an interface for a Polulu Tic stepper motor.

See https://www.pololu.com/docs/0J71/12 for the API reference.
"""

import subprocess
import time
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

    def __init__(
        self,
        num_steps_per_revolution: int,
        step_mode: PoluluTicMotorStepMode,
        max_current: float,
        max_degrees_per_second: float,
    ) -> None:
        self.num_steps_per_revolution = num_steps_per_revolution
        self.step_mode = step_mode
        self.send_command(["--step-mode", str(step_mode.value)])
        self.send_command(["--current", str(int(max_current * 1000))])
        max_speed = max_degrees_per_second * self.num_steps_per_revolution * self.step_mode.value * 10000 / 360
        self.send_command(["--max-speed", str(int(max_speed))])

    def status(self) -> str:
        """Returns the status of the motor."""
        return self.send_command(["--status", "--full"])

    def home(self) -> None:
        """Homes the device.

        Homing requires a configured limit switch.
        See https://www.pololu.com/docs/0J71/4.14.
        """
        self.send_command(["--exit-safe-start", "--energize"])
        self._wait_for_motor(ready=True, timeout=5)
        self.send_command(["--home", "fwd"])
        self._wait_for_motor(homing=True)

    def position(self) -> float:
        """Returns the position of the motor in degrees."""
        status = yaml.safe_load(self.status())
        return self._microstep_to_position(status["Current position"])

    def move_to(self, position: float) -> None:
        """Move the motor to the desired angle.

        Args:
            position: Absolute position in degrees.
        """
        target_position = self._position_to_microsteps(position)
        self.send_command([
            "--exit-safe-start",
            "--energize",
            "--position",
            str(target_position),
        ])
        self._wait_for_motor(position=target_position)

    def move_by(self, position: float) -> None:
        """Move the motor by the desired angle.

        Args:
            position: Relative position in degrees.
        """
        self.move_by(self.position() + position)

    def stop(self) -> None:
        """Stops the motion."""
        self.send_command(["--halt-and-hold"])

    @staticmethod
    def list_devices() -> str:
        """Lists all connected devices.

        Returns:
            The raw list of devices.
        """
        return PoluluTicMotor.send_command(["--list"])

    @staticmethod
    def send_command(args: list[str]) -> str:
        try:
            result = subprocess.run(
                ["ticcmd", *args],
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

    def _position_to_microsteps(self, value: float) -> int:
        """Converts from units of degrees to units of microsteps.

        Args:
            value: Value in degrees.
        """
        return int(value * self.num_steps_per_revolution * self.step_mode / 360)

    def _wait_for_motor(
        self,
        position: int = 0,
        homing: bool = False,
        ready: bool = False,
        timeout: float = 300,
    ) -> None:
        """Waits for readiness or completion.

        Args:
            position: Position in microsteps.
            homing: If true, wait until the homing is complete.
            ready: If true, wait until the motor is ready.
            timeout: Timeout in seconds.
        """
        deadline = time.monotonic() + timeout
        try:
            while time.monotonic() < deadline:
                self.send_command(["--reset-command-timeout"])
                status = yaml.safe_load(self.status())
                state = status["Operation state"]
                if state not in ("Normal", "Starting up"):
                    raise RuntimeError(f"Failed to move motor: {status}")
                if state == "Normal":
                    if ready:
                        return
                    if homing:
                        if not status["Homing active"]:
                            if status["Position uncertain"]:
                                raise RuntimeError("Failed to complete homing.")
                            return
                    elif (status["Current position"] == position and
                          status["Current velocity"] == 0):
                        return
                time.sleep(0.1)
            raise TimeoutError(f"Motor motion exceeded {timeout} seconds.")
        except (Exception, KeyboardInterrupt):
            self.stop()
            raise
