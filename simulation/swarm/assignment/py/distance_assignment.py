"""The distance assignment class assigns each interceptor to the nearest threat
that has not been assigned yet.
"""

from collections import namedtuple

import numpy as np

from simulation.swarm.assignment.py.assignment_interface import Assignment
from simulation.swarm.interceptor.py.interceptor_interface import Interceptor
from simulation.swarm.threat.py.threat_interface import Threat


class DistanceAssignment(Assignment):
    """Assignment based on distance.

    Each interceptor is assigned to the closest unassigned threat. After all
    threats have been assigned, the remaining interceptors will double up on
    threats.
    """

    # Interceptor-threat distance named tuple type.
    InterceptorThreatDistance = namedtuple(
        "InterceptorThreatDistance",
        ["interceptor_index", "threat_index", "distance"])

    def __init__(self, interceptors: list[Interceptor],
                 threats: list[Threat]) -> None:
        super().__init__(interceptors, threats)

    def _assign_threats(self) -> None:
        """Assigns each interceptor to a threat."""
        assignable_interceptor_indices = self.get_assignable_interceptor_indices(
            self.interceptors)
        if len(assignable_interceptor_indices) == 0:
            return
        active_threat_indices = self.get_active_threat_indices(self.threats)
        if len(active_threat_indices) == 0:
            return

        # Get the interceptor and threat positions.
        interceptor_positions = [
            self.interceptors[interceptor_index].get_position()
            for interceptor_index in assignable_interceptor_indices
        ]
        threat_positions = [
            self.threats[threat_index].get_position()
            for threat_index in active_threat_indices
        ]

        # Sort the interceptor-threat distances.
        interceptor_threat_distances = []
        for assignable_interceptor_index, interceptor_index in enumerate(
                assignable_interceptor_indices):
            for active_threat_index, threat_index in enumerate(
                    active_threat_indices):
                distance = (np.linalg.norm(
                    threat_positions[active_threat_index] -
                    interceptor_positions[assignable_interceptor_index]))
                interceptor_threat_distances.append(
                    DistanceAssignment.InterceptorThreatDistance(
                        interceptor_index=interceptor_index,
                        threat_index=threat_index,
                        distance=distance,
                    ))
        sorted_interceptor_threat_distances = sorted(
            interceptor_threat_distances, key=lambda x: x.distance)

        # Assign threats to interceptors based on distance.
        while len(sorted_interceptor_threat_distances) > 0:
            assigned_interceptor_indices = set()
            assigned_threat_indices = set()
            for (interceptor_index, threat_index,
                 distance) in sorted_interceptor_threat_distances:
                if (interceptor_index not in assigned_interceptor_indices and
                        threat_index not in assigned_threat_indices):
                    self.interceptor_to_threat_assignments[
                        interceptor_index] = threat_index
                    assigned_interceptor_indices.add(interceptor_index)
                    assigned_threat_indices.add(threat_index)
            sorted_interceptor_threat_distances = set(
                filter(
                    lambda x: x.interceptor_index not in
                    assigned_interceptor_indices,
                    sorted_interceptor_threat_distances))
