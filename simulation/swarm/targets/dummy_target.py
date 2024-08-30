"""The dummy target class represents the dynamics of a single dummy target."""

from simulation.swarm.proto.target_config_pb2 import TargetConfig
from simulation.swarm.targets.target_interface import Target


class DummyTarget(Target):
    """Dummy target dynamics."""

    def __init__(self, target_config: TargetConfig) -> None:
        super().__init__(target_config)

    def update(self, t: float) -> None:
        """Updates the agent's state according to the environment.

        Args:
            t: Time in seconds.
        """
        # The dummy target does not accelerate.
        return
