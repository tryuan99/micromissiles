"""The micromissile class represents the dynamics of a single micromissile."""

import google.protobuf
import numpy as np
from simulation.swarm.proto.agent_pb2 import AgentConfig
from simulation.swarm.proto.sensor_pb2 import SensorOutput
from simulation.swarm.proto.static_config_pb2 import StaticConfig

from simulation.swarm.interceptor.py.interceptor_interface import Interceptor


class Micromissile(Interceptor):
    """Micromissile dynamics."""

    # Proportional navigation gain.
    PROPORTIONAL_NAVIGATION_GAIN = 3

    def __init__(
        self,
        interceptor_config: AgentConfig,
        ready: bool = True,
        t_creation: float = 0,
    ) -> None:
        super().__init__(interceptor_config, ready, t_creation)

    @property
    def static_config(self) -> StaticConfig:
        """Returns the static configuration of the micromissile."""
        static_config_file_path = (
            "simulation/swarm/configs/interceptor/micromissile.pbtxt")
        with open(static_config_file_path, "r") as static_config_file:
            static_config = google.protobuf.text_format.Parse(
                static_config_file.read(), StaticConfig())
        return static_config

    def _update(self, t: float) -> None:
        """Updates the agent's state in the midcourse and terminal flight
        phase.

        The interceptor uses proportional navigation to intercept the threat,
        i.e., it should maintain a constant azimuth and elevation to the threat.

        Args:
            t: Time in seconds.
        """
        if self.has_assigned_threat():
            # Update the threat model.
            model_step_time = t - self.threat_model.state_update_time
            self.threat_model.update(t)
            self.threat_model.step(self.threat_model.state_update_time,
                                   model_step_time)

            # Correct the state of the threat model at the sensor frequency.
            sensor_update_period = 1 / self.dynamic_config.sensor_config.frequency
            if t - self.sensor_update_time >= sensor_update_period:
                # TODO(titan): Use some guidance filter to estimate the state from
                # the sensor output.
                self.threat_model.set_state(self.threat.state)
                self.sensor_update_time = t

            # Sense the threat.
            sensor_output = self.sensor.sense([self.threat_model])[0]

            # Check whether the threat has been hit.
            if self.has_hit_threat():
                # Consider the kill probability of the threat.
                kill_probability = (
                    self.threat.static_config.hit_config.kill_probability)
                if np.random.binomial(1, kill_probability) > 0:
                    self.mark_as_hit()
                    self.threat.mark_as_hit()
                    return

            # Calculate the acceleration input.
            acceleration_input = self._calculate_acceleration_input(
                sensor_output)
        else:
            acceleration_input = np.zeros(3)

        # Calculate and set the total acceleration.
        acceleration = self._calculate_total_acceleration(acceleration_input)
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
        closing_velocity = -sensor_output.velocity.range

        # Get the normalized principal axes of the interceptor.
        normalized_roll, normalized_pitch, normalized_yaw = (
            self.get_normalized_principal_axes())

        # Calculate the desired acceleration vector. The interceptor cannot
        # accelerate along the roll axis.
        acceleration_input = (self.PROPORTIONAL_NAVIGATION_GAIN *
                              (azimuth_velocity * normalized_pitch +
                               elevation_velocity * normalized_yaw) *
                              closing_velocity)

        # Clamp the acceleration vector.
        max_acceleration = self._get_max_acceleration()
        if np.linalg.norm(acceleration_input) > max_acceleration:
            return (acceleration_input / np.linalg.norm(acceleration_input) *
                    max_acceleration)
        return acceleration_input
