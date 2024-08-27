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

    # Maximum acceleration in m/s^2.
    MAX_ACCELERATION = 300 * constants.STANDARD_GRAVITY

    # Coefficient for proportional navigation.
    PROPORTIONAL_NAVIGATION_COEFFICIENT = 3

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
        azimuth_velocity = sensor_output.velocity.azimuth
        elevation_velocity = sensor_output.velocity.elevation

        # Get the principal axes of the missile.
        roll, lateral, yaw = self.get_principal_axes()

        # Normalize the vectors pointing in the three axes.
        normalized_lateral = lateral / np.linalg.norm(lateral)
        normalized_yaw = yaw / np.linalg.norm(yaw)

        # Calculate the components along the three axes.
        lateral_coefficient = (np.cos(elevation_velocity) *
                               np.sin(azimuth_velocity))
        yaw_coefficient = np.sin(elevation_velocity)

        # Calculate the desired acceleration vector. The missile cannot
        # accelerate along the roll axis.
        acceleration_input_vector = (lateral_coefficient * normalized_lateral +
                                     yaw_coefficient * normalized_yaw)

        # Limit the acceleration vector.
        acceleration_input_vector /= np.linalg.norm(acceleration_input_vector)
        acceleration_input_vector *= self.MAX_ACCELERATION

        # Set the acceleration according to the feedback law.
        acceleration_vector = acceleration_input_vector
        (self.state.acceleration.x, self.state.acceleration.y,
         self.state.acceleration.z) = acceleration_vector
