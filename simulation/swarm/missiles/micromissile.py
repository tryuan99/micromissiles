"""The micromissile class represents the dynamics of a single micromissile."""

import google.protobuf
import numpy as np

from simulation.swarm import constants
from simulation.swarm.missiles.missile_interface import Missile
from simulation.swarm.proto.missile_config_pb2 import MissileConfig
from simulation.swarm.proto.sensor_pb2 import SensorOutput
from simulation.swarm.proto.static_config_pb2 import StaticConfig


class Micromissile(Missile):
    """Micromissile dynamics."""

    # Coefficient for proportional navigation.
    PROPORTIONAL_NAVIGATION_COEFFICIENT = 3

    def __init__(self, missile_config: MissileConfig) -> None:
        super().__init__(missile_config)

    @property
    def static_config(self) -> StaticConfig:
        """Returns the static configuration of the micromissile."""
        static_config_file_path = (
            "simulation/swarm/configs/missiles/micromissile.pbtxt")
        with open(static_config_file_path, "r") as static_config_file:
            static_config = google.protobuf.text_format.Parse(
                static_config_file.read(), StaticConfig())
        return static_config

    def _update_boost(self, t: float) -> None:
        """Updates the agent's state in the boost flight phase.

        During the boost phase, we assume that the missile will only accelerate
        along its roll axis.

        Args:
            t: Time in seconds.
        """
        normalized_roll, normalized_lateral, normalized_yaw = (
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

    def _update(self, t: float) -> None:
        """Updates the agent's state in the midcourse and terminal flight
        phase.

        The missile uses proportional navigation to intercept the target, i.e.,
        it should maintain a constant azimuth and elevation to the target.

        Args:
            t: Time in seconds.
        """
        if self.target is None:
            return

        # Update the target model.
        model_step_time = t - self.target_model.state_update_time
        self.target_model.update(t)
        self.target_model.step(self.target_model.state_update_time,
                               model_step_time)

        # Correct the state of the target model at the sensor frequency.
        sensor_update_period = 1 / self.dynamic_config.sensor_config.frequency
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
                self.target.static_config.hit_config.kill_probability)
            if np.random.binomial(1, kill_probability) > 0:
                self.set_hit()
                self.target.set_hit()
                return

        # Calculate the acceleration input.
        acceleration_input = self._calculate_acceleration_input(sensor_output)

        # Calculate and set the total acceleration.
        acceleration = self._calculate_total_acceleration(
            acceleration_input, compensate_for_gravity=True)
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
