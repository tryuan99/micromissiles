"""The motor class is an interface for stepper motors."""

from abc import ABC, abstractmethod


class Motor(ABC):
    """Interface for a stepper motor."""

    @abstractmethod
    def status(self) -> list[str]:
        """Returns the status of the motor."""

    @abstractmethod
    def position(self) -> float:
        """Returns the position of the motor in degrees."""

    @abstractmethod
    def move_to(self, position: float) -> None:
        """Move the motor to the desired angle.

        Args:
            position: Absolute position in degrees.
        """

    @abstractmethod
    def move_by(self, position: float) -> None:
        """Move the motor by the desired angle.

        Args:
            position: Relative position in degrees.
        """
