"""The assignment class is an interface for assigning a target to each missile."""

from abc import ABC, abstractmethod

from simulation.swarm.missiles.py.missile_interface import Missile
from simulation.swarm.targets.py.target_interface import Target


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
