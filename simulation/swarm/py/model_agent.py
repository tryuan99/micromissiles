"""The model agent models an agent and has no configuration."""

from simulation.swarm.proto.state_pb2 import State
from simulation.swarm.proto.static_config_pb2 import StaticConfig

from simulation.swarm.py.agent import Agent


class ModelAgent(Agent):
    """Dummy agent."""

    def __init__(
        self,
        initial_state: State,
    ) -> None:
        super().__init__(initial_state=initial_state)

    @property
    def static_config(self) -> StaticConfig:
        """Returns the static configuration of the agent."""
        return StaticConfig()
