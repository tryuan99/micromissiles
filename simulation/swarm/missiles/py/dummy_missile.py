"""The dummy missile class represents the dynamics of a single dummy missile."""

from simulation.swarm.proto.missile_config_pb2 import MissileConfig
from simulation.swarm.proto.static_config_pb2 import StaticConfig

from simulation.swarm.missiles.py.missile_interface import Missile


class DummyMissile(Missile):
    """Dummy missile dynamics."""

    def __init__(
        self,
        missile_config: MissileConfig,
        ready: bool = True,
        t_creation: float = 0,
    ) -> None:
        super().__init__(missile_config, ready, t_creation)

    @property
    def static_config(self) -> StaticConfig:
        """Returns the static configuration of the ."""
        return StaticConfig()

    def assignable_to_target(self) -> bool:
        """Returns whether a target can be assigned to the missile."""
        return True
