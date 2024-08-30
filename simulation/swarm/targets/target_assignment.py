"""The target assignment class assigns each missile to a target."""

from abc import ABC, abstractmethod

import numpy as np

from simulation.swarm.missiles.missile import Missile
from simulation.swarm.targets.target import Target


class TargetAssignment(ABC):
    """Target assignment interface.

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


class DistanceBasedTargetAssignment(TargetAssignment):
    """Target assignment based on distance.

    Each missile is assigned to the closest unassigned target. After all
    targets have been assigned, the remaining missiles will double up on
    targets.
    """

    def __init__(self, missiles: list[Missile], targets: list[Target]) -> None:
        super().__init__(missiles, targets)

    def _assign_targets(self) -> None:
        """Assigns each missile to a target."""
        # Get the missile and target positions.
        missile_positions = [
            missile.get_position() for missile in self.missiles
        ]
        target_positions = [target.get_position() for target in self.targets]

        # Sort the missile-target distances.
        missile_target_distances = []
        for missile_index, missile_position in enumerate(missile_positions):
            if not self.missiles[missile_index].has_assigned_target():
                for target_index, target_position in enumerate(
                        target_positions):
                    distance = (np.linalg.norm(target_position -
                                               missile_position))
                    missile_target_distances.append((
                        missile_index,
                        target_index,
                        distance,
                    ))
        sorted_missile_target_distances = sorted(missile_target_distances,
                                                 key=lambda x: x[2])

        # Assign targets to missiles based on distance.
        while len(sorted_missile_target_distances) > 0:
            assigned_missile_indices = set()
            assigned_target_indices = set()
            for (missile_index, target_index,
                 distance) in sorted_missile_target_distances:
                if (missile_index not in assigned_missile_indices and
                        target_index not in assigned_target_indices):
                    self.missile_to_target_assignments[
                        missile_index] = target_index
                    assigned_missile_indices.add(missile_index)
                    assigned_target_indices.add(target_index)
            sorted_missile_target_distances = set(
                filter(lambda x: x[0] not in assigned_missile_indices,
                       sorted_missile_target_distances))
