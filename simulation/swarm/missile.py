"""The missile class represents the dynamics of a single missile."""

import numpy as np

from simulation.swarm.agent import Agent
from simulation.swarm.proto.missile_config_pb2 import MissileConfig
from simulation.swarm.sensor import IdealSensor
from simulation.swarm.target import Target


class Missile(Agent):
    """Missile dynamics.

    Attributes:
        sensor: The sensor mounted on the missile.
        target: The target assigned to the missile.
        bearing: The azimuth and elevation to the target.
    """

    # Proportional coefficient for the controller.
    KP = 10000

    def __init__(self, missile_config: MissileConfig) -> None:
        super().__init__(missile_config.initial_state)
        self.sensor = IdealSensor(self)
        self.target: Target = None
        self.bearing: tuple[float, float] = None

    def assign(self, target: Target) -> None:
        """Assigns the given target to the missile.

        Args:
            target: Target to assign to the missile.
        """
        self.target = target

    def update(self) -> None:
        """Updates the agent's state according to the environment.

        The missile uses proportional navigation to intercept the target, i.e.,
        it should maintain a constant azimuth and elevation to the target.
        """
        if self.target is None:
            return

        # Sense the target.
        sensor_output = self.sensor.sense([self.target])[0]
        azimuth = sensor_output.position.azimuth
        elevation = sensor_output.position.elevation

        if self.bearing is None:
            self.bearing = (azimuth, elevation)
            return

        # TODO(titan): Add limitations to the steering capabilities of the
        # missile.
        azimuth_prev, elevation_prev = self.bearing
        error_azimuth = azimuth - azimuth_prev
        error_elevation = elevation - elevation_prev

        # Find the normal vector to the missile's plane.
        roll = np.array([
            self.state.velocity.x,
            self.state.velocity.y,
            self.state.velocity.z,
        ])
        # The lateral axis is to the missile's starboard.
        lateral = np.array([roll[1], -roll[0], 0])
        normal = np.cross(lateral, roll)

        # Normalize the vectors pointing in the three axes.
        normalized_roll = roll / np.linalg.norm(roll)
        normalized_lateral = lateral / np.linalg.norm(lateral)
        normalized_yaw = normal / np.linalg.norm(normal)

        # Calculate the components along the three axes.
        roll_coefficient = np.cos(error_elevation) * np.cos(error_azimuth)
        lateral_coefficient = np.cos(error_elevation) * np.sin(error_azimuth)
        yaw_coefficient = np.sin(error_elevation)

        # Calculate the desired acceleration vector.
        acceleration_vector = (roll_coefficient * normalized_roll +
                               lateral_coefficient * normalized_lateral +
                               yaw_coefficient * normalized_yaw)

        # Set the acceleration according to the feedback law.
        (self.state.acceleration.x, self.state.acceleration.y,
         self.state.acceleration.z) = self.KP * acceleration_vector
