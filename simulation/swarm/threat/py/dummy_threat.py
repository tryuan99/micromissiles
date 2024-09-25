"""The dummy threat class represents the dynamics of a single dummy threat."""

from simulation.swarm.proto.agent_pb2 import AgentConfig
from simulation.swarm.proto.static_config_pb2 import StaticConfig

from simulation.swarm.threat.py.threat_interface import Threat


class DummyThreat(Threat):
    """Dummy threat dynamics."""

    def __init__(
        self,
        threat_config: AgentConfig,
        ready: bool = True,
        t_creation: float = 0,
    ) -> None:
        super().__init__(threat_config, ready, t_creation)

    @property
    def static_config(self) -> StaticConfig:
        """Returns the static configuration of the threat."""
        return StaticConfig()
