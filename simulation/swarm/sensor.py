"""The sensor class is an interface for a missile's sensing system."""

from abc import ABC, abstractmethod

import numpy as np

from simulation.swarm.agent import Agent
from simulation.swarm.proto.sensor_pb2 import SensorOutput


class Sensor(ABC):
    """Sensing system.

    Attributes:
        agent: The agent on which the sensor is mounted.
    """

    def __init__(self, agent: Agent) -> None:
        self.agent = agent

    @abstractmethod
    def sense(self, targets: list[Agent]) -> list[SensorOutput]:
        """Senses the targets.

        The azimuth and elevation are relative to the agent's velocity assuming
        that the lateral axis is parallel to the x-y plane.
        TODO(titan): The sensor output should be relative to the agent's roll,
        pitch, and yaw.

        Args:
            targets: List of targets to sense.

        Returns:
            A list of sensor outputs for the targets.
        """


class IdealSensor(Sensor):
    """Ideal sensor.

    The ideal sensor senses the targets perfectly with no bias or variance.
    """

    def sense(self, targets: list[Agent]) -> list[SensorOutput]:
        """Senses the targets.

        The azimuth and elevation are relative to the agent's velocity assuming
        that the lateral axis is parallel to the x-y plane.
        TODO(titan): The sensor output should be relative to the agent's roll,
        pitch, and yaw.

        Args:
            targets: List of targets to sense.

        Returns:
            A list of sensor outputs for the targets.
        """
        output = [SensorOutput() for _ in range(len(targets))]
        position = np.array([
            self.agent.state.position.x,
            self.agent.state.position.y,
            self.agent.state.position.z,
        ])
        # The roll axis is assumed to be aligned with the agent's velocity
        # vector.
        roll = np.array([
            self.agent.state.velocity.x,
            self.agent.state.velocity.y,
            self.agent.state.velocity.z,
        ])
        # The lateral axis is to the agent's starboard.
        lateral = np.array([roll[1], -roll[0], 0])
        normal = np.cross(lateral, roll)
        for target_index, target in enumerate(targets):
            target_position = np.array([
                target.state.position.x,
                target.state.position.y,
                target.state.position.z,
            ])
            difference = target_position - position
            target_velocity = np.array([
                target.state.velocity.x,
                target.state.velocity.y,
                target.state.velocity.z,
            ])

            # Calculate the distance to the target.
            output[target_index].position.range = np.linalg.norm(difference)

            # Project the difference vector onto the normal vector.
            difference_projection_on_normal = (np.dot(difference, normal) /
                                               np.linalg.norm(normal)**2 *
                                               normal)
            # Project the difference vector onto the agent's plane.
            difference_projection_on_plane = (difference -
                                              difference_projection_on_normal)

            # Determine the sign of the elevation.
            if np.dot(difference_projection_on_normal, normal) > 0:
                elevation_sign = 1
            else:
                elevation_sign = -1

            # Calculate the elevation to the target.
            output[target_index].position.elevation = (
                elevation_sign * np.arctan(
                    np.linalg.norm(difference_projection_on_normal) /
                    np.linalg.norm(difference_projection_on_plane)))

            # Project the projection onto the roll axis.
            difference_projection_on_roll = (
                np.dot(difference_projection_on_plane, roll) /
                np.linalg.norm(roll)**2 * roll)
            # Find the projection onto the lateral axis.
            difference_projection_on_lateral = (difference_projection_on_plane -
                                                difference_projection_on_roll)

            # Determine the sign of the azimuth.
            azimuth_cross = np.cross(difference_projection_on_lateral,
                                     difference_projection_on_roll)
            if np.dot(azimuth_cross, normal) > 0:
                azimuth_sign = 1
            else:
                azimuth_sign = -1

            # Calculate the azimuth to the target.
            output[target_index].position.azimuth = azimuth_sign * np.arctan(
                np.linalg.norm(difference_projection_on_lateral) /
                np.linalg.norm(difference_projection_on_roll))
        return output
