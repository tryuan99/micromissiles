"""The assignment class is an interface for assigning a target to each missile."""

from abc import ABC, abstractmethod

from simulation.swarm.missile.py.missile_interface import Missile
from simulation.swarm.target.py.target_interface import Target


class Assignment(ABC):
    """Assignment interface.

    Missiles with a previously assigned target are ignored.

    Attributes:
        missiles: A list of missiles.
        targest: A list of targets.
        missile_to_target_assignment: A map from the missile index to its
          assigned target index.
    """

    def __init__(self, missiles: list[Missile], targets: list[Target]) -> None:
        self.missiles = missiles
        self.targets = targets
        self.missile_to_target_assignments: dict[int, int] = {}
        self._assign_targets()

    @abstractmethod
    def _assign_targets(self) -> None:
        """Assigns each missile to a target."""

    @staticmethod
    def get_assignable_missile_indices(missiles: list[Missile]) -> list[int]:
        """Returns the indices of assignable missiles.

        Args:
            missiles: List of missiles.

        Returns:
            The list of assignable missile indices.
        """
        assignable_missile_indices = [
            missile_index for missile_index, missile in enumerate(missiles)
            if missile.assignable_to_target()
        ]
        return assignable_missile_indices

    @staticmethod
    def get_active_target_indices(targets: list[Target]) -> list[int]:
        """Returns the indices of active targets.

        Args:
            targets: List of targets.

        Returns:
            The list of active target indices.
        """
        active_target_indices = [
            target_index for target_index, target in enumerate(targets)
            if not target.hit
        ]
        return active_target_indices
