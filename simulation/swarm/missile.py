"""The missile class represents the dynamics of a single missile."""

import numpy as np

from simulation.swarm import constants
from simulation.swarm.agent import Agent, ModelAgent
from simulation.swarm.proto.missile_config_pb2 import MissileConfig
from simulation.swarm.proto.sensor_pb2 import SensorOutput
from simulation.swarm.sensor import IdealSensor
from simulation.swarm.target import Target


class Missile(Agent):
    """Missile dynamics.

    Attributes:
        sensor: The sensor mounted on the missile.
        sensor_update_time: The time of the last sensor update.
        target: The target assigned to the missile.
        target_model: The model of the target.
    """

    # Coefficient for proportional navigation.
    PROPORTIONAL_NAVIGATION_COEFFICIENT = 3

    def __init__(self, missile_config: MissileConfig) -> None:
        super().__init__(missile_config)
        self.sensor = IdealSensor(self)
        self.sensor_update_time = -np.inf
        self.target: Target = None
        self.target_model: Agent = None

    def assign_target(self, target: Target) -> None:
        """Assigns the given target to the missile.

        Args:
            target: Target to assign to the missile.
        """
        self.target = target
        self.target_model = ModelAgent(target.state)

    def has_assigned_target(self) -> bool:
        """Returns whether a target is assigned to the missile."""
        return self.target is not None

    def unassign_target(self) -> None:
        """Unassigns the given target from the missile."""
        self.target = None
        self.target_model = None

    def has_hit_target(self) -> bool:
        """Checks whether the missile has hit the assigned target.

        Returns:
            Whether the missile has hit the target.
        """
        if self.target is None:
            return False

        # Determine the distance to the target.
        position = self.get_position()
        target_position = self.target.get_position()
        distance = np.linalg.norm(target_position - position)

        # A hit is recorded if the target is within the missile's hit radius.
        hit_radius = self.physical_config.hit_config.hit_radius
        if distance <= hit_radius:
            return True

    def update(self, t: float) -> None:
        """Updates the agent's state according to the environment.

        The missile uses proportional navigation to intercept the target, i.e.,
        it should maintain a constant azimuth and elevation to the target.

        Args:
            t: Time in seconds.
        """
        if self.target is None:
            return

        # Update the target model.
        model_step_time = t - self.target_model.update_time
        self.target_model.update(t)
        self.target_model.step(self.target_model.update_time, model_step_time)

        # Correct the state of the target model at the sensor frequency.
        sensor_update_period = 1 / self.physical_config.sensor_config.frequency
        if t - self.sensor_update_time >= sensor_update_period:
            # TODO(titan): Use some guidance filter to estimate the state from
            # the sensor output.
            self.target_model.set_state(self.target.state)
            self.sensor_update_time = t

        # Sense the target.
        sensor_output = self.sensor.sense([self.target_model])[0]

        # Check whether the target has been hit.
        if self.has_hit_target():
            # Consider the kill probability of the target.
            kill_probability = (
                self.target.physical_config.hit_config.kill_probability)
            if np.random.binomial(1, kill_probability) > 0:
                self.hit = True
                self.target.hit = True
                return

        # Determine the acceleration input.
        acceleration_input = self._calculate_acceleration_input(sensor_output)

        # Determine the gravity and compensate for it.
        gravity = self.get_gravity()
        gravity_projection_on_lateral_and_yaw = (
            self._calculate_gravity_projection_on_lateral_and_yaw())
        acceleration_input -= gravity_projection_on_lateral_and_yaw

        # Calculate the air drag.
        air_drag_acceleration = self._calculate_drag()
        # Calculate the lift-induced drag.
        lift_induced_drag_acceleration = (
            self._calculate_lift_induced_drag(acceleration_input))
        # Calculate the total drag acceleration.
        normalized_roll, normalized_lateral, normalized_yaw = (
            self.get_normalized_principal_axes())
        drag_acceleration = (
            -(air_drag_acceleration + lift_induced_drag_acceleration) *
            normalized_roll)

        # Set the acceleration vector.
        acceleration = acceleration_input + gravity + drag_acceleration
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
            The gravity acceleration in m/s^2 along the lateral and yaw axes.
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

    def _calculate_drag(self) -> float:
        """Calculates the air drag.

        Returns:
            The drag acceleration in m/s^2.
        """
        drag_coefficient = (
            self.physical_config.lift_drag_config.drag_coefficient)
        cross_sectional_area = (
            self.physical_config.body_config.cross_sectional_area)
        mass = self.physical_config.body_config.mass

        dynamic_pressure = self.get_dynamic_pressure()
        drag_force = drag_coefficient * dynamic_pressure * cross_sectional_area
        drag_acceleration = drag_force / mass
        return drag_acceleration

    def _calculate_lift_induced_drag(self,
                                     acceleration_input: np.ndarray) -> float:
        """Calculates the lift-induced drag.

        Args:
            acceleration_input: The x, y, and z acceleration inputs in m/s^2.

        Returns:
            The drag acceleration in m/s^2.
        """
        # Project the acceleration input onto the yaw axis.
        normalized_roll, normalized_lateral, normalized_yaw = (
            self.get_normalized_principal_axes())
        lift_acceleration = np.dot(acceleration_input, normalized_yaw)

        # Calculate the drag acceleration from the lift acceleration.
        lift_drag_ratio = (
            self.physical_config.lift_drag_config.lift_drag_ratio)
        lift_induced_drag_acceleration = (np.abs(lift_acceleration /
                                                 lift_drag_ratio))
        return lift_induced_drag_acceleration

    def _get_max_acceleration(self) -> float:
        """Calculates the maximum acceleration of the missile based on its
        velocity.

        Returns:
            The maximum acceleration in m/s^2.
        """
        max_reference_acceleration = (
            self.physical_config.acceleration_config.max_reference_acceleration
            * constants.STANDARD_GRAVITY)
        reference_speed = (
            self.physical_config.acceleration_config.reference_speed)
        # The maximum acceleration scales with the squared speed.
        max_acceleration = ((self.get_speed() / reference_speed)**2 *
                            max_reference_acceleration)
        return max_acceleration
