"""The interceptor class represents an interceptor model."""

import numpy as np

from simulation.swarm.reachability import constants
from simulation.swarm.reachability.agent import Agent
from simulation.swarm.reachability.model import PredictionModel
from simulation.swarm.reachability.state import State


class Interceptor(Agent):
    """Interceptor model.

    The acceleration command is subject to maximum acceleration bounds, gravity,
    air drag, lift-induced drag, and ground avoidance maneuvers.
    """

    def total_acceleration(
        self,
        state: State,
        acceleration: np.ndarray,
    ) -> np.ndarray:
        """Returns the total acceleration for the applied acceleration command.

        Args:
            state: Agent state.
            acceleration: Acceleration command in m/s^2.
        """
        forward = state.forward
        acceleration_with_ground_avoidance = self._avoid_ground(
            acceleration, state)
        # The interceptor always accelerates forward at the maximum forward
        # acceleration to maximize the speed and thus the agility.
        acceleration_with_thrust = (constants.project_off_axis(
            acceleration_with_ground_avoidance,
            forward,
        ) + self.max_forward_acceleration() * forward)
        limited_acceleration = self.limit_acceleration_input(
            acceleration_with_thrust,
            forward,
            state.speed,
        )
        gravity = constants.gravity_vector()
        drag = -(self._air_drag(state) +
                 self._lift_induced_drag(limited_acceleration, forward))
        return limited_acceleration + gravity + drag * forward

    def prediction_model(self, state: State) -> PredictionModel:
        """Returns the linearized prediction model at the state.

        Args:
            state: Agent state.
        """
        # The plant always applies the maximum forward acceleration a against
        # the air drag k * v^2, so the speed follows v' = a - k * v^2. Its exact
        # solution is v(t) = (v0 + a * s) / (1 + k * v0 * s), where
        # s = tanh(sqrt(a * k) * t) / sqrt(a * k), which tends to t as a * k
        # tends to zero.
        speed = state.speed
        acceleration = self.max_forward_acceleration()
        drag_per_speed_squared = self._drag_per_speed_squared(state)
        rate = np.sqrt(acceleration * drag_per_speed_squared)

        def speed_profile(times: np.ndarray) -> np.ndarray:
            """Returns the predicted speed under thrust and air drag.

            Args:
                times: Elapsed times in seconds.

            Returns:
                The predicted speeds in m/s at the given times.
            """
            effective_times = (np.tanh(rate * times) /
                               rate if rate > 0 else times)
            return ((speed + acceleration * effective_times) /
                    (1 + drag_per_speed_squared * speed * effective_times))

        return self._prediction_model(
            state,
            acceleration_bias=constants.gravity_vector(),
            max_forward_acceleration=0.0,
            speed_profile=speed_profile,
        )

    def _air_drag(self, state: State) -> float:
        """Returns the air drag deceleration in m/s^2 at the state.

        Args:
            state: Agent state.
        """
        return self._drag_per_speed_squared(state) * state.speed**2

    def _drag_per_speed_squared(self, state: State) -> float:
        """Returns the air drag deceleration per speed squared in 1/m.

        Args:
            state: Agent state.
        """
        lift_drag = self.static_config.lift_drag_config
        body = self.static_config.body_config
        return (0.5 * constants.air_density_at_altitude(state.position[1]) *
                lift_drag.drag_coefficient * body.cross_sectional_area /
                body.mass)

    def _lift_induced_drag(
        self,
        acceleration: np.ndarray,
        forward: np.ndarray,
    ) -> float:
        """Returns the lift-induced drag deceleration for the applied acceleration.

        Args:
            acceleration: Acceleration in m/s^2.
            forward: Forward direction.
        """
        lift_acceleration = np.linalg.norm(
            constants.project_off_axis(acceleration, forward))
        return np.abs(lift_acceleration /
                      self.static_config.lift_drag_config.lift_drag_ratio)

    def _avoid_ground(
        self,
        acceleration: np.ndarray,
        state: State,
    ) -> np.ndarray:
        """Returns the command blended with an upward pull near the ground.

        Args:
            acceleration: Acceleration in m/s^2.
            state: Agent state.
        """
        vertical_speed = state.velocity[1]
        altitude = state.position[1]
        threshold = (np.abs(vertical_speed) *
                     constants.GROUND_PROXIMITY_THRESHOLD_FACTOR +
                     0.5 * constants.GRAVITY *
                     constants.GROUND_PROXIMITY_THRESHOLD_FACTOR**2)
        if vertical_speed < 0 and altitude < threshold:
            blend_factor = 1.0 - altitude / threshold
            body_up = constants.normalize_vector(
                constants.project_off_axis(constants.UP, state.forward))
            return acceleration + (blend_factor * self.max_normal_acceleration(
                state.speed) * body_up)
        return acceleration
