"""The Hydra-70 class represents the dynamics of a single unguided Hydra-70 rocket."""

import google.protobuf
import numpy as np
from simulation.swarm.proto.agent_pb2 import AgentConfig, InterceptorType
from simulation.swarm.proto.static_config_pb2 import StaticConfig

from simulation.swarm.interceptor.py.interceptor_interface import Interceptor
from simulation.swarm.interceptor.py.micromissile import Micromissile
from simulation.swarm.utils.py import constants

# Hydra-70 submunitions type enumeration to the interceptor class.
HYDRA_70_SUBMUNITIONS_TYPE_ENUM_TO_CLASS = {
    InterceptorType.MICROMISSILE: Micromissile,
}


class Hydra70(Interceptor):
    """Hydra-70 dynamics.

    Attributes:
        has_spawned: A boolean indicating whether the rocket has spawned submunitions.
    """

    def __init__(
        self,
        interceptor_config: AgentConfig,
        ready: bool = True,
        t_creation: float = 0,
    ) -> None:
        super().__init__(interceptor_config, ready, t_creation)
        self.has_spawned = False

    @property
    def static_config(self) -> StaticConfig:
        """Returns the static configuration of the Hydra-70 rocket."""
        static_config_file_path = (
            "simulation/swarm/configs/interceptor/hydra_70.pbtxt")
        with open(static_config_file_path, "r") as static_config_file:
            static_config = google.protobuf.text_format.Parse(
                static_config_file.read(), StaticConfig())
        return static_config

    def assignable_to_threat(self) -> bool:
        """Returns whether a threat can be assigned to the interceptor."""
        return False

    def spawn(self, t: float) -> list[Interceptor]:
        """Spawns new interceptors.

        Args:
            t: Time in seconds.

        Returns:
            A list of newly spawned interceptors.
        """
        if self.has_spawned:
            return []

        num_submunitions = self.submunitions_config.num_submunitions
        launch_time = self.dynamic_config.launch_config.launch_time
        submunitions_launch_time = (
            self.submunitions_config.launch_config.launch_time)
        if t >= self.t_creation + launch_time + submunitions_launch_time:
            # Define the interceptor configuration for the submunitions.
            submunitions_type = self.submunitions_config.agent_config.interceptor_type
            submunitions_interceptor_config = AgentConfig()
            submunitions_interceptor_config.CopyFrom(
                self.submunitions_config.agent_config)
            submunitions_interceptor_config.initial_state.CopyFrom(self.state)

            # Create the interceptors for the submunitions.
            spawned_interceptors = [
                HYDRA_70_SUBMUNITIONS_TYPE_ENUM_TO_CLASS[submunitions_type](
                    submunitions_interceptor_config, t_creation=t)
                for _ in range(num_submunitions)
            ]
            self.has_spawned = True
            return spawned_interceptors
        return []

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
