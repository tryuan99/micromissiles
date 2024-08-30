"""The target class represents the dynamics of a single target."""

from simulation.swarm.agent import Agent
from simulation.swarm.proto.target_config_pb2 import TargetConfig


class Target(Agent):
    """Target dynamics."""

    def __init__(self, target_config: TargetConfig) -> None:
        super().__init__(target_config)

    def update(self, t: float) -> None:
        """Updates the agent's state according to the environment.

        Args:
            t: Time in seconds.
        """
        # The target does not accelerate.
        return
