"""The closest approach class tracks the continuous closest approach during the
engagement.
"""

import numpy as np


class ClosestApproach:
    """Tracks continuous closest approach between the agents.

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

    @staticmethod
    def first_contact_fraction(
        start_offset: np.ndarray,
        end_offset: np.ndarray,
        radius: float,
    ) -> float | None:
        """Returns the first entry into a radius along a straight segment.

        The contact fraction is in [0, 1]. It is zero when initially within the
        radius, or None if the segment never reaches the radius.

        Args:
            start_offset: Relative position at the segment start in meters,
                with shape (3,).
            end_offset: Relative position at the segment end in meters,
                with shape (3,).
            radius: Nonnegative contact radius in meters.
        """
        squared_distance_from_contact = (np.dot(start_offset, start_offset) -
                                         radius**2)
        if squared_distance_from_contact <= 0:
            return 0.0
        segment_displacement = end_offset - start_offset
        squared_segment_length = np.dot(segment_displacement,
                                        segment_displacement)
        if squared_segment_length == 0:
            return None
        offset_displacement_dot = np.dot(start_offset, segment_displacement)
        discriminant = (offset_displacement_dot**2 -
                        squared_segment_length * squared_distance_from_contact)
        if offset_displacement_dot >= 0 or discriminant < 0:
            return None
        # This form avoids cancellation when the segment starts near contact.
        fraction = squared_distance_from_contact / (-offset_displacement_dot +
                                                    np.sqrt(discriminant))
        return fraction if 0 <= fraction <= 1 else None

    def update(
        self,
        start_offset: np.ndarray,
        end_offset: np.ndarray,
        start_time: float,
        time_step: float,
    ) -> None:
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
        delta_squared = np.dot(delta, delta)
        if delta_squared < 1e-18:
            fraction = 0.0
        else:
            fraction = min(
                1.0, max(0.0, -np.dot(start_offset, delta) / delta_squared))
        separation = np.linalg.norm(start_offset + fraction * delta)
        if separation < self.separation:
            self.separation = separation
            self.time = start_time + fraction * time_step
