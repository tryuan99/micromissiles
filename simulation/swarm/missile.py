"""The missile class represents the dynamics of a single missile."""

import numpy as np

from simulation.swarm import constants
from simulation.swarm.agent import Agent
from simulation.swarm.proto.missile_config_pb2 import MissileConfig
from simulation.swarm.sensor import IdealSensor
from simulation.swarm.target import Target


class Missile(Agent):
    """Missile dynamics.

    Attributes:
        sensor: The sensor mounted on the missile.
        target: The target assigned to the missile.
    """

    # Proportional coefficient for the controller.
    KP = 100000

    def __init__(self, missile_config: MissileConfig) -> None:
        super().__init__(missile_config.initial_state)
        self.sensor = IdealSensor(self)
        self.target: Target = None

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

        TODO(titan): Add limitations to the steering capabilities of the
        missile.
        """
        if self.target is None:
            return

        # Sense the target.
        sensor_output = self.sensor.sense([self.target])[0]

        # In proportional navigation, the acceleration vector should be
        # proportional to the rate of change of the bearing.
        error_azimuth_velocity = sensor_output.velocity.azimuth
        error_elevation_velocity = sensor_output.velocity.elevation

        # Get the principal axes of the missile.
        roll, lateral, yaw = self.get_principal_axes()

        # Normalize the vectors pointing in the three axes.
        normalized_roll = roll / np.linalg.norm(roll)
        normalized_lateral = lateral / np.linalg.norm(lateral)
        normalized_yaw = yaw / np.linalg.norm(yaw)

        # Calculate the components along the three axes.
        roll_coefficient = (np.cos(error_elevation_velocity) *
                            np.cos(error_azimuth_velocity))
        lateral_coefficient = (np.cos(error_elevation_velocity) *
                               np.sin(error_azimuth_velocity))
        yaw_coefficient = np.sin(error_elevation_velocity)

        # Calculate the desired acceleration vector.
        normalized_acceleration_input_vector = (
            roll_coefficient * normalized_roll +
            lateral_coefficient * normalized_lateral +
            yaw_coefficient * normalized_yaw)
        acceleration_input_vector = (self.KP *
                                     normalized_acceleration_input_vector)

        # Add gravity.
        gravity_vector = np.array(
            [0, 0, -constants.gravity_at_altitude(self.state.position.z)])

        # Set the acceleration according to the feedback law.
        acceleration_vector = acceleration_input_vector + gravity_vector
        (self.state.acceleration.x, self.state.acceleration.y,
         self.state.acceleration.z) = acceleration_vector
