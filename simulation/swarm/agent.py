"""The agent class is an interface for a missile or a target."""

from abc import ABC, abstractmethod

import numpy as np
import scipy.integrate

from simulation.swarm.proto.state_pb2 import State


class Agent(ABC):
    """Agent.

    Attributes:
        state: Current state.
        history: A list of 2-tuples consisting of a timestamp and the state.
    """

    def __init__(self, initial_state: State) -> None:
        self.state = initial_state
        self.history = [(0, State())]
        self.history[-1][1].CopyFrom(initial_state)

    def step(self, t_start: float, t_step: float) -> None:
        """Steps forward the simulation by simulating the dynamics of the
        agent.

        This function mutates the agent's state variable.
        TODO(titan): Evolve the agent's roll, pitch, and yaw.

        Args:
            t_start: Start time in seconds.
            t_step: Step time in seconds.
        """
        # Update the most recent state in the history of states.
        self.history[-1][1].CopyFrom(self.state)

        initial_state = np.array([
            self.state.position.x,
            self.state.position.y,
            self.state.position.z,
            self.state.velocity.x,
            self.state.velocity.y,
            self.state.velocity.z,
        ])

        def kinematics(t: float, state: np.ndarray) -> np.ndarray:
            """Defines the kinematic equations of the agent.

            Args:
                t: Time in seconds.
                state: Current state vector.

            Returns:
                The time derivative of the state vector at the given time.
            """
            (
                position_x,
                position_y,
                position_z,
                velocity_x,
                velocity_y,
                velocity_z,
            ) = state
            dx = np.array([
                # dx/dt = vx
                velocity_x,
                # dy/dt = vy
                velocity_y,
                # dz/dt = vz
                velocity_z,
                # dvx/dt = ax
                self.state.acceleration.x,
                # dvy/dt = ay
                self.state.acceleration.y,
                # dvz/dt = az
                self.state.acceleration.z,
            ])
            return dx

        solution = scipy.integrate.solve_ivp(
            fun=kinematics,
            t_span=[0, t_step],
            y0=initial_state,
            t_eval=[t_step],
        )
        (
            position_x,
            position_y,
            position_z,
            velocity_x,
            velocity_y,
            velocity_z,
        ) = np.squeeze(solution.y)
        self.state.position.x = position_x
        self.state.position.y = position_y
        self.state.position.z = position_z
        self.state.velocity.x = velocity_x
        self.state.velocity.y = velocity_y
        self.state.velocity.z = velocity_z

        # Add the new state to the history of states.
        self.history.append((t_start + t_step, State()))
        self.history[-1][1].CopyFrom(self.state)

    @abstractmethod
    def update(self) -> None:
        """Updates the agent's state according to the environment."""
