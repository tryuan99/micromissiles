"""Interceptor dynamics."""

import casadi

from simulation.swarm.reachability import constants
from simulation.swarm.reachability.agent import Agent
from simulation.swarm.reachability.state import State


class Interceptor(Agent):
    """Interceptor dynamics."""

    def _total_acceleration(
        self,
        state: State,
        command: casadi.SX | casadi.MX,
    ) -> casadi.SX | casadi.MX:
        """Returns the total acceleration with ground avoidance.

        Args:
            state: Flight state with position, velocity, and rotation.
            command: Acceleration command in m/s^2 with shape (3,).
        """
        max_normal_acceleration = self.max_normal_acceleration(state.speed)
        threshold = (casadi.fabs(state.velocity[1]) *
                     constants.GROUND_PROXIMITY_THRESHOLD_FACTOR +
                     0.5 * constants.GRAVITY *
                     constants.GROUND_PROXIMITY_THRESHOLD_FACTOR**2)
        pull = (1 - state.position[1] /
                threshold) * max_normal_acceleration * state.up
        acceleration_command = command + casadi.if_else(
            casadi.logic_and(state.velocity[1] < 0, state.position[1]
                             < threshold), pull, casadi.SX.zeros(3))
        limited_acceleration = super()._total_acceleration(
            state, acceleration_command)
        air_density = constants.AIR_DENSITY_SEA_LEVEL * casadi.exp(
            -state.position[1] / constants.AIR_DENSITY_SCALE_HEIGHT)
        air_drag = (0.5 * air_density *
                    self.static_config.lift_drag_config.drag_coefficient *
                    self.static_config.body_config.cross_sectional_area /
                    self.static_config.body_config.mass * state.speed**2)
        lift_induced_drag = casadi.fabs(
            constants.casadi_vector_norm(
                constants.casadi_project_off_axis(limited_acceleration,
                                                  state.forward)) /
            self.static_config.lift_drag_config.lift_drag_ratio)
        return (limited_acceleration + casadi.DM(constants.gravity_vector()) -
                (air_drag + lift_induced_drag) * state.forward)
