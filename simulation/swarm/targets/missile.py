"""The missile class represents the dynamics of a single missile."""

import google.protobuf

from simulation.swarm.proto.static_config_pb2 import StaticConfig
from simulation.swarm.proto.target_config_pb2 import TargetConfig
from simulation.swarm.targets.target_interface import Target


class Missile(Target):
    """Missile dynamics."""

    def __init__(self, target_config: TargetConfig) -> None:
        super().__init__(target_config)

    @property
    def static_config(self) -> StaticConfig:
        """Returns the static configuration of the missile."""
        static_config_file_path = "simulation/swarm/configs/targets/missile.pbtxt"
        with open(static_config_file_path, "r") as static_config_file:
            static_config = google.protobuf.text_format.Parse(
                static_config_file.read(), StaticConfig())
        return static_config
