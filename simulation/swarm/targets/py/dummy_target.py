"""The dummy target class represents the dynamics of a single dummy target."""

from simulation.swarm.proto.agent_pb2 import AgentConfig
from simulation.swarm.proto.static_config_pb2 import StaticConfig

from simulation.swarm.targets.py.target_interface import Target


class DummyTarget(Target):
    """Dummy target dynamics."""

    def __init__(
        self,
        target_config: AgentConfig,
        ready: bool = True,
        t_creation: float = 0,
    ) -> None:
        super().__init__(target_config, ready, t_creation)

    @property
    def static_config(self) -> StaticConfig:
        """Returns the static configuration of the target."""
        return StaticConfig()
