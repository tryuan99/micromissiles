"""Threat dynamics."""

import casadi

from simulation.swarm.reachability import constants
from simulation.swarm.reachability.agent import Agent
from simulation.swarm.reachability.state import State


class Threat(Agent):
    """Threat dynamics."""

    def _total_acceleration(
        self,
        state: State,
        command: casadi.SX | casadi.MX,
    ) -> casadi.SX | casadi.MX:
        """Returns the total acceleration.

        Args:
            state: Flight state with position, velocity, and rotation.
            command: Acceleration command in m/s^2 with shape (3,).
        """
        forward = casadi.dot(command, state.forward) * state.forward
        normal = constants.casadi_project_off_axis(command, state.forward)
        speed_error = self.max_speed() - state.speed
        acceleration_command = normal + casadi.if_else(
            casadi.fabs(speed_error) < constants.SPEED_ERROR_THRESHOLD,
            casadi.SX.zeros(3), forward * casadi.sign(speed_error))
        return super()._total_acceleration(state, acceleration_command)
