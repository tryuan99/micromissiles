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
        self.interceptor_states.append(
            np.concatenate(
                [interceptor_state.position, interceptor_state.velocity]))
        self.threat_states.append(
            np.concatenate([threat_state.position, threat_state.velocity]))

    def arrays(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Returns the (times, interceptor states, threat states) as arrays.

        Timestamps have shape (samples,). Each state array has shape
        (samples, 6), with position in meters and velocity in m/s.
        """
        return (
            np.asarray(self.times, dtype=float),
            np.asarray(self.interceptor_states, dtype=float).reshape(-1, 6),
            np.asarray(self.threat_states, dtype=float).reshape(-1, 6),
        )
