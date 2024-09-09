"""The drone class represents the dynamics of a single drone."""

import google.protobuf
from simulation.swarm.proto.agent_pb2 import AgentConfig
from simulation.swarm.proto.static_config_pb2 import StaticConfig

from simulation.swarm.targets.py.target_interface import Target


class Drone(Target):
    """Drone dynamics."""

    def __init__(
        self,
        target_config: AgentConfig,
        ready: bool = True,
        t_creation: float = 0,
    ) -> None:
        super().__init__(target_config, ready, t_creation)

    @property
    def static_config(self) -> StaticConfig:
        """Returns the static configuration of the drone."""
        static_config_file_path = (
            "simulation/swarm/configs/targets/drone.pbtxt")
        with open(static_config_file_path, "r") as static_config_file:
            static_config = google.protobuf.text_format.Parse(
                static_config_file.read(), StaticConfig())
        return static_config
