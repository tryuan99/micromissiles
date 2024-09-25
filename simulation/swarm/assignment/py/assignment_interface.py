"""The assignment class is an interface for assigning a threat to each interceptor."""

from abc import ABC, abstractmethod

from simulation.swarm.interceptor.py.interceptor_interface import Interceptor
from simulation.swarm.threat.py.threat_interface import Threat


class Assignment(ABC):
    """Assignment interface.

    Interceptors with a previously assigned threat are ignored.

    Attributes:
        interceptors: A list of interceptors.
        threats: A list of threats.
        interceptor_to_threat_assignment: A map from the interceptor index to its
          assigned threat index.
    """

    def __init__(self, interceptors: list[Interceptor],
                 threats: list[Threat]) -> None:
        self.interceptors = interceptors
        self.threats = threats
        self.interceptor_to_threat_assignments: dict[int, int] = {}
        self._assign_threats()

    @abstractmethod
    def _assign_threats(self) -> None:
        """Assigns each interceptor to a threat."""

    @staticmethod
    def get_assignable_interceptor_indices(
            interceptors: list[Interceptor]) -> list[int]:
        """Returns the indices of assignable interceptors.

        Args:
            interceptors: List of interceptors.

        Returns:
            The list of assignable interceptor indices.
        """
        assignable_interceptor_indices = [
            interceptor_index
            for interceptor_index, interceptor in enumerate(interceptors)
            if interceptor.assignable_to_threat()
        ]
        return assignable_interceptor_indices

    @staticmethod
    def get_active_threat_indices(threats: list[Threat]) -> list[int]:
        """Returns the indices of active threats.

        Args:
            threats: List of threats.

        Returns:
            The list of active threat indices.
        """
        active_threat_indices = [
            threat_index for threat_index, threat in enumerate(threats)
            if not threat.hit
        ]
        return active_threat_indices
