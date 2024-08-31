"""The Hydra-70 class represents the dynamics of a single unguided Hydra-70 rocket."""

import google.protobuf
import numpy as np

from simulation.swarm import constants
from simulation.swarm.missiles.missile_interface import Missile
from simulation.swarm.proto.missile_config_pb2 import MissileConfig
from simulation.swarm.proto.static_config_pb2 import StaticConfig


class Hydra70(Missile):
    """Hydra-70 dynamics."""

    def __init__(self, missile_config: MissileConfig) -> None:
        super().__init__(missile_config)

    @property
    def static_config(self) -> StaticConfig:
        """Returns the static configuration of the Hydra-70 rocket."""
        static_config_file_path = (
            "simulation/swarm/configs/missiles/hydra_70.pbtxt")
        with open(static_config_file_path, "r") as static_config_file:
            static_config = google.protobuf.text_format.Parse(
                static_config_file.read(), StaticConfig())
        return static_config

    def _update_boost(self, t: float) -> None:
        """Updates the agent's state in the boost flight phase.

        During the boost phase, we assume that the missile will only accelerate
        along its roll axis.

        Args:
            t: Time in seconds.
        """
        normalized_roll, normalized_lateral, normalized_yaw = (
            self.get_normalized_principal_axes())
        boost_acceleration = (
            self.static_config.boost_config.boost_acceleration *
            constants.STANDARD_GRAVITY)
        acceleration_input = boost_acceleration * normalized_roll

        # Calculate and set the total acceleration.
        acceleration = self._calculate_total_acceleration(
            acceleration_input, compensate_for_gravity=False)
        (
            self.state.acceleration.x,
            self.state.acceleration.y,
            self.state.acceleration.z,
        ) = acceleration

    def _update(self, t: float) -> None:
        """Updates the agent's state in the midcourse and terminal flight
        phase.

        Args:
            t: Time in seconds.
        """
        # The Hydra-70 rocket is unguided, so only consider gravity and drag.
        acceleration_input = np.zeros(3)
        acceleration = self._calculate_total_acceleration(acceleration_input)
        (
            self.state.acceleration.x,
            self.state.acceleration.y,
            self.state.acceleration.z,
        ) = acceleration
