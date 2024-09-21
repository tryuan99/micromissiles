"""The missile class is an interface for the dynamics of a single missile."""

from abc import ABC

import numpy as np
from simulation.swarm.proto.agent_pb2 import AgentConfig

from simulation.swarm.py.agent import Agent
from simulation.swarm.py.model_agent import ModelAgent
from simulation.swarm.sensor.py.sensor import SENSOR_TYPE_ENUM_TO_CLASS
from simulation.swarm.target.py.target_interface import Target
from simulation.swarm.utils.py import constants


class Missile(Agent, ABC):
    """Missile dynamics.

    Attributes:
        sensor: The sensor mounted on the missile.
        sensor_update_time: The time of the last sensor update.
        target: The target assigned to the missile.
        target_model: The model of the target.
    """

    def __init__(
        self,
        missile_config: AgentConfig,
        ready: bool = True,
        t_creation: float = 0,
    ) -> None:
        super().__init__(missile_config, ready, t_creation)
        sensor_class = (
            SENSOR_TYPE_ENUM_TO_CLASS[self.dynamic_config.sensor_config.type])
        self.sensor = sensor_class(self)
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

    def assignable_to_target(self) -> bool:
        """Returns whether a target can be assigned to the missile."""
        return self.has_launched() and not self.has_assigned_target()

    def check_target(self) -> None:
        """Checks whether the target has been hit.

        If the target has been hit, unassign the target.
        """
        if self.has_assigned_target() and self.target.hit:
            self.unassign_target()

    def unassign_target(self) -> None:
        """Unassigns the given target from the missile."""
        self.target = None
        self.target_model = None

    def has_hit_target(self) -> bool:
        """Checks whether the missile has hit the assigned target.

        Returns:
            Whether the missile has hit the target.
        """
        if not self.has_assigned_target():
            return False

        # Determine the distance to the target.
        position = self.get_position()
        target_position = self.target.get_position()
        distance = np.linalg.norm(target_position - position)

        # A hit is recorded if the target is within the missile's hit radius.
        hit_radius = self.static_config.hit_config.hit_radius
        return distance <= hit_radius

    def _update_ready(self, t: float) -> None:
        """Updates the missile's state in the ready flight phase.

        Args:
            t: Time in seconds.
        """
        # The missile is subject to gravity and drag with zero input
        # acceleration.
        acceleration_input = np.zeros(3)

        # Calculate and set the total acceleration.
        acceleration = self._calculate_total_acceleration(acceleration_input)
        (
            self.state.acceleration.x,
            self.state.acceleration.y,
            self.state.acceleration.z,
        ) = acceleration

    def _update_boost(self, t: float) -> None:
        """Updates the missile's state in the boost flight phase.

        During the boost phase, we assume that the missile will only accelerate
        along its roll axis.

        Args:
            t: Time in seconds.
        """
        normalized_roll, normalized_pitch, normalized_yaw = (
            self.get_normalized_principal_axes())
        boost_acceleration = (
            self.static_config.boost_config.boost_acceleration *
            constants.STANDARD_GRAVITY)
        acceleration_input = boost_acceleration * normalized_roll

        # Calculate and set the total acceleration.
        acceleration = self._calculate_total_acceleration(acceleration_input)
        (
            self.state.acceleration.x,
            self.state.acceleration.y,
            self.state.acceleration.z,
        ) = acceleration

    def _calculate_gravity_projection_on_pitch_and_yaw(self) -> np.ndarray:
        """Calculates the gravity projection on the pitch and yaw axes.

        The missile can only compensate for gravity along the pitch and yaw
        axes.

        Returns:
            The gravity acceleration in m/s^2 along the pitch and yaw axes.
        """
        normalized_roll, normalized_pitch, normalized_yaw = (
            self.get_normalized_principal_axes())
        gravity = self.get_gravity()

        # Project the gravity onto the pitch and yaw axes.
        gravity_projection_pitch_coefficient = np.dot(gravity, normalized_pitch)
        gravity_projection_yaw_coefficient = np.dot(gravity, normalized_yaw)
        gravity_projection_on_pitch_and_yaw = (
            gravity_projection_pitch_coefficient * normalized_pitch +
            gravity_projection_yaw_coefficient + normalized_yaw)
        return gravity_projection_on_pitch_and_yaw

    def _calculate_drag(self) -> float:
        """Calculates the air drag.

        Returns:
            The drag acceleration in m/s^2.
        """
        drag_coefficient = (
            self.static_config.lift_drag_config.drag_coefficient)
        cross_sectional_area = (
            self.static_config.body_config.cross_sectional_area)
        mass = self.static_config.body_config.mass

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
        normalized_roll, normalized_pitch, normalized_yaw = (
            self.get_normalized_principal_axes())
        lift_acceleration = np.linalg.norm(
            acceleration_input -
            np.dot(acceleration_input, normalized_roll) * normalized_roll)

        # Calculate the drag acceleration from the lift acceleration.
        lift_drag_ratio = self.static_config.lift_drag_config.lift_drag_ratio
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
            self.static_config.acceleration_config.max_reference_acceleration *
            constants.STANDARD_GRAVITY)
        reference_speed = self.static_config.acceleration_config.reference_speed
        # The maximum acceleration scales with the squared speed.
        max_acceleration = ((self.get_speed() / reference_speed)**2 *
                            max_reference_acceleration)
        return max_acceleration

    def _calculate_total_acceleration(
            self,
            acceleration_input: np.ndarray,
            compensate_for_gravity: bool = False) -> np.ndarray:
        """Calculates the total acceleration vector, including gravity and drag.

        Args:
            acceleration_input: Acceleration input vector.
            compensate_for_gravity: If true, compensate for gravity.

        Returns:
            The total x, y, and z acceleration components.
        """
        # Determine the gravity and compensate for it.
        gravity = self.get_gravity()
        if compensate_for_gravity:
            gravity_projection_on_pitch_and_yaw = (
                self._calculate_gravity_projection_on_pitch_and_yaw())
            compensated_acceleration_input = (
                acceleration_input - gravity_projection_on_pitch_and_yaw)
        else:
            compensated_acceleration_input = acceleration_input

        # Calculate the air drag.
        air_drag_acceleration = self._calculate_drag()
        # Calculate the lift-induced drag.
        lift_induced_drag_acceleration = (
            self._calculate_lift_induced_drag(compensated_acceleration_input))
        # Calculate the total drag acceleration.
        normalized_roll, normalized_pitch, normalized_yaw = (
            self.get_normalized_principal_axes())
        drag_acceleration = (
            -(air_drag_acceleration + lift_induced_drag_acceleration) *
            normalized_roll)

        # Calculate the total acceleration vector.
        acceleration = (compensated_acceleration_input + gravity +
                        drag_acceleration)
        return acceleration
