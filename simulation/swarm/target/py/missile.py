"""The missile class represents the dynamics of a single missile."""

import google.protobuf
from simulation.swarm.proto.agent_pb2 import AgentConfig
from simulation.swarm.proto.static_config_pb2 import StaticConfig

from simulation.swarm.target.py.target_interface import Target


class Missile(Target):
    """Missile dynamics."""

    def __init__(
        self,
        target_config: AgentConfig,
        ready: bool = True,
        t_creation: float = 0,
    ) -> None:
        super().__init__(target_config, ready, t_creation)

    @property
    def static_config(self) -> StaticConfig:
        """Returns the static configuration of the missile."""
        static_config_file_path = "simulation/swarm/configs/target/missile.pbtxt"
        with open(static_config_file_path, "r") as static_config_file:
            static_config = google.protobuf.text_format.Parse(
                static_config_file.read(), StaticConfig())
        return static_config
