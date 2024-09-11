"""The distance assignment class assigns each missile to the nearest target
that has not been assigned yet.
"""

from collections import namedtuple

import numpy as np

from simulation.swarm.assignment.py.assignment_interface import Assignment
from simulation.swarm.missile.py.missile_interface import Missile
from simulation.swarm.target.py.target_interface import Target


class DistanceAssignment(Assignment):
    """Assignment based on distance.

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
        assignable_missile_indices = self.get_assignable_missile_indices(
            self.missiles)
        if len(assignable_missile_indices) == 0:
            return
        active_target_indices = self.get_active_target_indices(self.targets)
        if len(active_target_indices) == 0:
            return

        # Get the missile and target positions.
        missile_positions = [
            self.missiles[missile_index].get_position()
            for missile_index in assignable_missile_indices
        ]
        target_positions = [
            self.targets[target_index].get_position()
            for target_index in active_target_indices
        ]

        # Sort the missile-target distances.
        missile_target_distances = []
        for assignable_missile_index, missile_index in enumerate(
                assignable_missile_indices):
            for active_target_index, target_index in enumerate(
                    active_target_indices):
                distance = (
                    np.linalg.norm(target_positions[active_target_index] -
                                   missile_positions[assignable_missile_index]))
                missile_target_distances.append(
                    DistanceAssignment.MissileTargetDistance(
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
