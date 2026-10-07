"""Named access to numerical and symbolic flight state vectors."""

import casadi
import numpy as np

from simulation.swarm.reachability import constants


class State:
    """Position, velocity, and body orientation backed by a CasADi vector.

    Numeric fields are NumPy arrays; symbolic fields retain CasADi expressions.

    Attributes:
        vector: Position, velocity, and xyzw quaternion with shape (10,).
        position: Position in meters with shape (3,).
        velocity: Velocity in m/s with shape (3,).
        rotation: Unit quaternion in xyzw order with shape (4,).
    """

    SIZE = 10

    def __init__(self, vector: casadi.SX | casadi.MX | casadi.DM) -> None:
        self.vector = vector
        if isinstance(vector, casadi.DM):
            rotation = vector[6:10]
            self.vector = casadi.vertcat(
                vector[:6], rotation / constants.casadi_vector_norm(rotation))

    @property
    def position(self) -> np.ndarray | casadi.SX | casadi.MX | casadi.DM:
        """Returns position in meters with shape (3,)."""
        return self._component(0, 3)

    @property
    def velocity(self) -> np.ndarray | casadi.SX | casadi.MX | casadi.DM:
        """Returns velocity in m/s with shape (3,)."""
        return self._component(3, 6)

    @property
    def rotation(self) -> np.ndarray | casadi.SX | casadi.MX | casadi.DM:
        """Returns the unit xyzw quaternion with shape (4,)."""
        return self._component(6, 10)

    @property
    def speed(self) -> float | casadi.SX | casadi.MX | casadi.DM:
        """Returns speed in m/s."""
        if isinstance(self.vector, casadi.DM):
            return np.linalg.norm(self.velocity)
        return constants.casadi_vector_norm(self.velocity)

    @property
    def forward(self) -> np.ndarray | casadi.SX | casadi.MX | casadi.DM:
        """Returns the body's forward direction."""
        forward = constants.casadi_rotate_vector(casadi.vertcat(self.rotation),
                                                 casadi.DM(constants.FORWARD))
        return (forward.full().reshape(3)
                if isinstance(forward, casadi.DM) else forward)

    @property
    def up(self) -> np.ndarray | casadi.SX | casadi.MX | casadi.DM:
        """Returns the body's up direction."""
        up = constants.casadi_rotate_vector(casadi.vertcat(self.rotation),
                                            casadi.DM(constants.UP))
        return up.full().reshape(3) if isinstance(up, casadi.DM) else up

    @classmethod
    def from_components(
        cls,
        position: np.ndarray | casadi.SX | casadi.MX | casadi.DM,
        velocity: np.ndarray | casadi.SX | casadi.MX | casadi.DM,
        rotation: np.ndarray | casadi.SX | casadi.MX | casadi.DM | None = None,
    ) -> "State":
        """Returns a state assembled from its named components.

        Args:
            position: Position in meters with shape (3,).
            velocity: Velocity in m/s with shape (3,).
            rotation: Unit xyzw quaternion, or None to align with velocity.
        """
        if rotation is None:
            rotation = constants.casadi_look_rotation(casadi.vertcat(velocity))
        return cls(casadi.vertcat(position, velocity, rotation))

    def to_array(self) -> np.ndarray:
        """Returns the numeric state vector."""
        return self.vector.full().reshape(-1)

    def interpolate(self, end_state: "State", fraction: float) -> "State":
        """Returns an interpolated state with normalized body orientation.

        Args:
            end_state: State at the segment end.
            fraction: Fraction along the segment, between zero and one.
        """
        return State(self.vector + fraction * (end_state.vector - self.vector))

    def _component(self, start: int,
                   end: int) -> np.ndarray | casadi.SX | casadi.MX | casadi.DM:
        """Returns a numeric or symbolic component of the state vector.

        Args:
            start: First component index.
            end: Exclusive end index.
        """
        component = self.vector[start:end]
        return (component.full().reshape(-1) if isinstance(
            component, casadi.DM) else component)
