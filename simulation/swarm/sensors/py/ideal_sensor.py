"""The ideal sensor class represents an ideal, omniscient sensor with no bias
or variance.
"""

import numpy as np
from simulation.swarm.proto.sensor_pb2 import SensorOutput

from simulation.swarm.py.agent import Agent
from simulation.swarm.sensors.py.sensor_interface import Sensor


class IdealSensor(Sensor):
    """Ideal sensor.

    The ideal sensor senses the targets perfectly with no bias or variance.
    """

    def sense(self, targets: list[Agent]) -> list[SensorOutput]:
        """Senses the targets.

        TODO(titan): The sensor output should be relative to the agent's roll,
        pitch, and yaw.

        Args:
            targets: List of targets to sense.

        Returns:
            A list of sensor outputs for the targets.
        """
        target_sensor_outputs = [SensorOutput() for _ in range(len(targets))]
        for target_index, target in enumerate(targets):
            # Sense the target's position.
            target_position_sensor_output = self.sense_position(target)
            target_sensor_outputs[target_index].MergeFrom(
                target_position_sensor_output)

            # Sense the target's velocity.
            target_velocity_sensor_output = self.sense_velocity(target)
            target_sensor_outputs[target_index].MergeFrom(
                target_velocity_sensor_output)
        return target_sensor_outputs

    def sense_position(self, target: Agent) -> SensorOutput:
        """Senses the position of a single target, including the range, the
        azimuth, and the elevation.

        TODO(titan): The sensor output should be relative to the agent's roll,
        pitch, and yaw.

        Args:
            target: Target for which to sense the position.

        Returns:
            The sensor output with the position field populated.
        """
        position_sensor_output = SensorOutput()
        normalized_roll, normalized_pitch, normalized_yaw = (
            self.agent.get_normalized_principal_axes())

        # Calculate the relative position of the target with respect to the
        # agent.
        position = self.agent.get_position()
        target_position = target.get_position()
        target_relative_position = target_position - position

        # Calculate the distance to the target.
        position_sensor_output.position.range = np.linalg.norm(
            target_relative_position)

        # Project the relative position vector onto the yaw axis.
        relative_position_projection_on_yaw = (
            np.dot(target_relative_position, normalized_yaw) * normalized_yaw)
        # Project the relative position vector onto the agent's roll-pitch
        # plane.
        relative_position_projection_on_roll_pitch_plane = (
            target_relative_position - relative_position_projection_on_yaw)

        # Determine the sign of the elevation.
        if np.dot(relative_position_projection_on_yaw, normalized_yaw) >= 0:
            elevation_sign = 1
        else:
            elevation_sign = -1

        # Calculate the elevation to the target.
        position_sensor_output.position.elevation = (elevation_sign * np.arctan(
            np.linalg.norm(relative_position_projection_on_yaw) /
            np.linalg.norm(relative_position_projection_on_roll_pitch_plane)))

        # Project the projection onto the roll axis.
        relative_position_projection_on_roll = (np.dot(
            relative_position_projection_on_roll_pitch_plane, normalized_roll) *
                                                normalized_roll)
        # Find the projection onto the pitch axis.
        relative_position_projection_on_pitch = (
            relative_position_projection_on_roll_pitch_plane -
            relative_position_projection_on_roll)

        if (np.linalg.norm(relative_position_projection_on_pitch) > 0 or
                np.linalg.norm(relative_position_projection_on_roll) > 0):
            # Determine the sign of the azimuth.
            if np.dot(relative_position_projection_on_pitch,
                      normalized_pitch) >= 0:
                azimuth_sign = 1
            else:
                azimuth_sign = -1

            # Calculate the azimuth to the target.
            position_sensor_output.position.azimuth = (azimuth_sign * np.arctan(
                np.linalg.norm(relative_position_projection_on_pitch) /
                np.linalg.norm(relative_position_projection_on_roll)))
        else:
            position_sensor_output.position.azimuth = 0
        return position_sensor_output

    def sense_velocity(self, target: Agent) -> SensorOutput:
        """Senses the velocity of a single target, including the range rate,
        the azimuth rate of change, and the elevation rate of change.

        TODO(titan): The sensor output should be relative to the agent's roll,
        pitch, and yaw.

        Args:
            target: Target for which to sense the velocity.

        Returns:
            The sensor output with the velocity field populated.
        """
        velocity_sensor_output = SensorOutput()
        roll, pitch, yaw = self.agent.get_principal_axes()

        # Calculate the relative position of the target with respect to the
        # agent.
        position = self.agent.get_position()
        target_position = target.get_position()
        target_relative_position = target_position - position

        # Calculate the relative velocity of the target with respect to the
        # agent.
        velocity = self.agent.get_velocity()
        target_velocity = target.get_velocity()
        target_relative_velocity = target_velocity - velocity

        # Project the relative velocity vector onto the relative position
        # vector.
        velocity_projection_on_relative_position = (
            np.dot(target_relative_velocity, target_relative_position) /
            np.linalg.norm(target_relative_position)**2 *
            target_relative_position)

        # Determine the sign of the range rate.
        if np.dot(velocity_projection_on_relative_position,
                  target_relative_position) >= 0:
            range_rate_sign = 1
        else:
            range_rate_sign = -1

        # Calculate the range rate.
        velocity_sensor_output.velocity.range = (
            range_rate_sign *
            np.linalg.norm(velocity_projection_on_relative_position))

        # Project the relative velocity vector onto the sphere passing through
        # the target.
        velocity_projection_on_azimuth_elevation_sphere = (
            target_relative_velocity - velocity_projection_on_relative_position)

        # The target azimuth vector is orthogonal to the relative position
        # vector and points to the starboard of the target along the azimuth-
        # elevation sphere.
        target_azimuth = np.cross(target_relative_position, yaw)
        # The target elevation vector is orthogonal to the relative position
        # vector and points upwards from the target along the azimuth-
        # elevation sphere.
        target_elevation = np.cross(pitch, target_relative_position)
        # If the relative position vector is parallel to the yaw or pitch
        # axis, the target azimuth vector or the target elevation vector will
        # undefined.
        if np.linalg.norm(target_azimuth) == 0:
            target_azimuth = np.cross(target_relative_position,
                                      target_elevation)
        elif np.linalg.norm(target_elevation) == 0:
            target_elevation = np.cross(target_azimuth,
                                        target_relative_position)

        # Project the relative velocity vector on the azimuth-elevation sphere
        # onto the target azimuth vector.
        velocity_projection_on_target_azimuth = (
            np.dot(velocity_projection_on_azimuth_elevation_sphere,
                   target_azimuth) / np.linalg.norm(target_azimuth)**2 *
            target_azimuth)

        # Determine the sign of the azimuth velocity.
        if np.dot(velocity_projection_on_target_azimuth, target_azimuth) >= 0:
            azimuth_velocity_sign = 1
        else:
            azimuth_velocity_sign = -1

        # Calculate the time derivative of the azimuth to the target.
        velocity_sensor_output.velocity.azimuth = (
            azimuth_velocity_sign *
            np.linalg.norm(velocity_projection_on_target_azimuth) /
            np.linalg.norm(target_relative_position))

        # Project the velocity vector on the azimuth-elevation sphere onto
        # the target elevation vector.
        velocity_projection_on_target_elevation = (
            velocity_projection_on_azimuth_elevation_sphere -
            velocity_projection_on_target_azimuth)

        # Determine the sign of the elevation velocity.
        if np.dot(velocity_projection_on_target_elevation,
                  target_elevation) >= 0:
            elevation_velocity_sign = 1
        else:
            elevation_velocity_sign = -1

        # Calculate the time derivative of the elevation to the target.
        velocity_sensor_output.velocity.elevation = (
            elevation_velocity_sign *
            np.linalg.norm(velocity_projection_on_target_elevation) /
            np.linalg.norm(target_relative_position))
        return velocity_sensor_output
