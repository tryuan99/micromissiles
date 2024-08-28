"""The target class represents the dynamics of a single target."""

from simulation.swarm.agent import Agent
from simulation.swarm.proto.target_config_pb2 import TargetConfig


class Target(Agent):
    """Target dynamics."""

    def __init__(self, target_config: TargetConfig) -> None:
        super().__init__(target_config.initial_state)
        self.kill_probability = target_config.kill_probability

    def update(self) -> None:
        """Updates the agent's state according to the environment.

        The target does not accelerate.
        """
        return
