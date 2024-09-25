"""The threat class is an interface for the dynamics of a single threat."""

from abc import ABC

from simulation.swarm.proto.agent_pb2 import AgentConfig

from simulation.swarm.py.agent import Agent


class Threat(Agent, ABC):
    """Threat dynamics."""

    def __init__(
        self,
        threat_config: AgentConfig,
        ready: bool = True,
        t_creation: float = 0,
    ) -> None:
        super().__init__(threat_config, ready, t_creation)
