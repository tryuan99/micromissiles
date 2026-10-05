"""The state class represents the 6-DOF state of an agent."""

from dataclasses import dataclass

import numpy as np

from simulation.swarm.reachability import constants


@dataclass
class State:
    """A 6-DOF state comprising the position and velocity."""

    position: np.ndarray
    velocity: np.ndarray

    @property
    def speed(self) -> float:
        """Returns the speed in m/s."""
        return np.linalg.norm(self.velocity)

    @property
    def forward(self) -> np.ndarray:
        """Returns the unit velocity direction."""
        return constants.normalize_vector(self.velocity)

    def to_array(self) -> np.ndarray:
        """Returns the 6-length array."""
        return np.concatenate([self.position, self.velocity])

    @classmethod
    def from_array(cls, array: np.ndarray) -> "State":
        """Returns the state parsed from a 6-length array.

        Args:
            array: Position followed by the velocity.
        """
        array = np.asarray(array, dtype=float)
        return cls(position=array[:3].copy(), velocity=array[3:].copy())
