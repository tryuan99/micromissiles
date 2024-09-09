"""The target class is an interface for the dynamics of a single target."""

from abc import ABC

from simulation.swarm.proto.agent_pb2 import AgentConfig

from simulation.swarm.py.agent import Agent


class Target(Agent, ABC):
    """Target dynamics."""

    def __init__(
        self,
        target_config: AgentConfig,
        ready: bool = True,
        t_creation: float = 0,
    ) -> None:
        super().__init__(target_config, ready, t_creation)
