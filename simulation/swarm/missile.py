"""The missile class represents the dynamics of a single missile."""

import numpy as np

from simulation.swarm import constants
from simulation.swarm.agent import Agent
from simulation.swarm.proto.missile_config_pb2 import MissileConfig
from simulation.swarm.proto.sensor_pb2 import SensorOutput
from simulation.swarm.sensor import IdealSensor
from simulation.swarm.target import Target


class Missile(Agent):
    """Missile dynamics.

    Attributes:
        sensor: The sensor mounted on the missile.
        target: The target assigned to the missile.
    """

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
        """
        if self.target is None:
            return

        # Sense the target.
        sensor_output = self.sensor.sense([self.target])[0]

        # Determine the acceleration input.
        acceleration_input = self._calculate_acceleration_input(sensor_output)

        # Determine the gravity and compensate for it.
        gravity = self.get_gravity()
        gravity_projection_on_lateral_and_yaw = (
            self._calculate_gravity_projection_on_lateral_and_yaw())

        # Set the acceleration vector.
        acceleration = (acceleration_input -
                        gravity_projection_on_lateral_and_yaw + gravity)
        (
            self.state.acceleration.x,
            self.state.acceleration.y,
            self.state.acceleration.z,
        ) = acceleration

    def _calculate_acceleration_input(
            self, sensor_output: SensorOutput) -> np.ndarray:
        """Calculates the acceleration input to the sensor output.

        Args:
            sensor_output: Sensor output.

        Returns:
            The x, y, and z acceleration inputs in m/s^2.
        """
        # In proportional navigation, the acceleration vector should be
        # proportional to the rate of change of the bearing.
        azimuth_velocity = sensor_output.velocity.azimuth
        elevation_velocity = sensor_output.velocity.elevation

        # Get the normalized principal axes of the missile.
        normalized_roll, normalized_lateral, normalized_yaw = (
            self.get_normalized_principal_axes())

        # Calculate the components along the three axes.
        lateral_coefficient = (np.cos(elevation_velocity) *
                               np.sin(azimuth_velocity))
        yaw_coefficient = np.sin(elevation_velocity)

        # Calculate the desired acceleration vector. The missile cannot
        # accelerate along the roll axis.
        acceleration_input = (lateral_coefficient * normalized_lateral +
                              yaw_coefficient * normalized_yaw)

        # Limit the acceleration vector.
        acceleration_input /= np.linalg.norm(acceleration_input)
        acceleration_input *= self._get_max_acceleration()
        return acceleration_input

    def _calculate_gravity_projection_on_lateral_and_yaw(self) -> np.ndarray:
        """Calculates the gravity projection on the lateral and yaw axes.

        The missile can only compensate for gravity along the lateral and yaw
        axes.

        Returns:
            The gravity acceleration along the lateral and yaw axes.
        """
        normalized_roll, normalized_lateral, normalized_yaw = (
            self.get_normalized_principal_axes())
        gravity = self.get_gravity()

        # Project the gravity onto the lateral and yaw axes.
        gravity_projection_lateral_coefficient = np.dot(gravity,
                                                        normalized_lateral)
        gravity_projection_yaw_coefficient = np.dot(gravity, normalized_yaw)
        gravity_projection_on_lateral_and_yaw = (
            gravity_projection_lateral_coefficient * normalized_lateral +
            gravity_projection_yaw_coefficient + normalized_yaw)
        return gravity_projection_on_lateral_and_yaw

    def _get_max_acceleration(self) -> float:
        """Calculates the maximum acceleration of the missile based on its
        velocity.

        Returns:
            The maximum acceleration in m/s^2.
        """
        # Maximum acceleration in m/s^2 at 1 km/s.
        max_reference_acceleration = 300 * constants.STANDARD_GRAVITY
        reference_speed = 1000

        # Calculate the velocity.
        velocity = np.array([
            self.state.velocity.x,
            self.state.velocity.y,
            self.state.velocity.z,
        ])
        speed = np.linalg.norm(velocity)
        return (speed / reference_speed)**2 * max_reference_acceleration
