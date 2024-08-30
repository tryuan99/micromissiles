"""The dummy missile class represents the dynamics of a single dummy missile."""

from simulation.swarm.missiles.missile_interface import Missile
from simulation.swarm.proto.missile_config_pb2 import MissileConfig


class DummyMissile(Missile):
    """Dummy missile dynamics."""

    def __init__(self, missile_config: MissileConfig) -> None:
        super().__init__(missile_config)

    def update(self, t: float) -> None:
        """Updates the agent's state according to the environment.

        Args:
            t: Time in seconds.
        """
        # The dummy missile does not accelerate.
        return
