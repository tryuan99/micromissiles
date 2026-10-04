"""The closest approach class tracks the continuous closest approach during the
engagement.
"""

import numpy as np


class ClosestApproach:
    """The closest approach class tracks the closest approach during the
    engagement.

    Tracking only the positions at the discrete time steps would miss a
    crossing. Each time segment is thus treated as a straight segment and
    minimized analytically.

    Attributes:
        separation: Minimum separation in meters.
        time: Time of closest approach in seconds.
    """

    def __init__(self, initial_separation: float) -> None:
        self.separation = initial_separation
        self.time = 0.0

    def update(self, start_offset: np.ndarray, end_offset: np.ndarray,
               start_time: float, time_step: float) -> None:
        """Minimizes the separation over one time step.

        Args:
            start_offset: The relative position at the time step start in
                meters.
            end_offset: The relative position at the time step end in
                meters.
            start_time: The time at the time step start in seconds.
            time_step: The time step duration in seconds.
        """
        delta = end_offset - start_offset
        delta_squared = float(delta @ delta)
        if delta_squared < 1e-18:
            fraction = 0.0
        else:
            fraction = min(
                1.0, max(0.0, -float(start_offset @ delta) / delta_squared))
        separation = np.linalg.norm(start_offset + fraction * delta)
        if separation < self.separation:
            self.separation = separation
            self.time = start_time + fraction * time_step
