"""The target class is an interface for the dynamics of a single target."""

from abc import ABC

from simulation.swarm.agent import Agent
from simulation.swarm.proto.target_config_pb2 import TargetConfig


class Target(Agent, ABC):
    """Target dynamics."""

    def __init__(self, target_config: TargetConfig) -> None:
        super().__init__(target_config)
