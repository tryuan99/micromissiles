"""The dummy interceptor class represents the dynamics of a single dummy interceptor."""

from simulation.swarm.proto.agent_pb2 import AgentConfig
from simulation.swarm.proto.static_config_pb2 import StaticConfig

from simulation.swarm.interceptor.py.interceptor_interface import Interceptor


class DummyInterceptor(Interceptor):
    """Dummy interceptor dynamics."""

    def __init__(
        self,
        interceptor_config: AgentConfig,
        ready: bool = True,
        t_creation: float = 0,
    ) -> None:
        super().__init__(interceptor_config, ready, t_creation)

    @property
    def static_config(self) -> StaticConfig:
        """Returns the static configuration of the ."""
        return StaticConfig()

    def assignable_to_threat(self) -> bool:
        """Returns whether a threat can be assigned to the interceptor."""
        return True
