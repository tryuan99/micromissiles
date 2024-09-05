"""The target assignment class assigns each missile to a target."""

from abc import ABC, abstractmethod
from collections import namedtuple

import numpy as np

from simulation.swarm.missiles.py.missile_interface import Missile
from simulation.swarm.targets.py.target_interface import Target


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

    # Missile-target distance named tuple type.
    MissileTargetDistance = namedtuple(
        "MissileTargetDistance", ["missile_index", "target_index", "distance"])

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
            if self.missiles[missile_index].assignable_to_target():
                for target_index, target_position in enumerate(
                        target_positions):
                    if not self.targets[target_index].hit:
                        distance = (np.linalg.norm(target_position -
                                                   missile_position))
                        missile_target_distances.append(
                            DistanceBasedTargetAssignment.MissileTargetDistance(
                                missile_index=missile_index,
                                target_index=target_index,
                                distance=distance,
                            ))
        sorted_missile_target_distances = sorted(missile_target_distances,
                                                 key=lambda x: x.distance)

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
                filter(
                    lambda x: x.missile_index not in assigned_missile_indices,
                    sorted_missile_target_distances))
