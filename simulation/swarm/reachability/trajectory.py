"""The trajectory class accumulates the states of the interceptor and the
threat over the engagement.
"""

import numpy as np

from simulation.swarm.reachability.state import State


class Trajectory:
    """Trajectory of the interceptor and the threat.

    Attributes:
        times: List of time points.
        interceptor_states: List of interceptor states.
        threat_states: List of threat states.
    """

    def __init__(self) -> None:
        self.times: list[float] = []
        self.interceptor_states: list[np.ndarray] = []
        self.threat_states: list[np.ndarray] = []

    def append(
        self,
        time: float,
        interceptor_state: State,
        threat_state: State,
    ) -> None:
        """Records one sample of the interceptor and the threat states.

        Args:
            time: Simulation time in seconds.
            interceptor_state: Interceptor state.
            threat_state: Threat state.
        """
        self.times.append(time)
        self.interceptor_states.append(interceptor_state.to_array())
        self.threat_states.append(threat_state.to_array())

    def arrays(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Returns the (times, interceptor states, threat states) as arrays.

        Returns:
            A tuple consisting of the times with shape (N,) and the interceptor
            and threat states, each with shape (N, 6).
        """
        return (
            np.asarray(self.times, dtype=float),
            np.asarray(self.interceptor_states, dtype=float).reshape(-1, 6),
            np.asarray(self.threat_states, dtype=float).reshape(-1, 6),
        )
