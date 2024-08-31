"""The missile class is an interface for the dynamics of a single missile."""

from abc import ABC

import numpy as np

from simulation.swarm import constants
from simulation.swarm.agent import Agent, ModelAgent
from simulation.swarm.proto.missile_config_pb2 import MissileConfig
from simulation.swarm.sensors.sensor import SENSOR_TYPE_ENUM_TO_CLASS
from simulation.swarm.targets.target_interface import Target


class Missile(Agent, ABC):
    """Missile dynamics.

    Attributes:
        sensor: The sensor mounted on the missile.
        sensor_update_time: The time of the last sensor update.
        target: The target assigned to the missile.
        target_model: The model of the target.
    """

    def __init__(self, missile_config: MissileConfig) -> None:
        super().__init__(missile_config)
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
        hit_radius = self.static_config.hit_config.hit_radius
        if distance <= hit_radius:
            return True

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
        normalized_roll, normalized_lateral, normalized_yaw = (
            self.get_normalized_principal_axes())
        lift_acceleration = np.dot(acceleration_input, normalized_yaw)

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
