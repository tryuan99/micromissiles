"""The agent class is an interface for a missile or a target."""

from abc import ABC, abstractmethod

import numpy as np
import scipy.integrate

from simulation.swarm import constants
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

    def get_principal_axes(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Returns the principal axes of the agent.

        The principal axis directions have not been normalized.
        The roll axis is assumed to be aligned with the agent's velocity vector,
        and the lateral axis points to the starboard of the agent.
        TODO(titan): The roll axis does not necessarily have to be aligned with
        the agent's velocity vector.

        Returns:
            A 3-tuple consisting of the roll, lateral, and yaw axes.
        """
        # The roll axis is assumed to be aligned with the agent's velocity
        # vector.
        roll = np.array([
            self.state.velocity.x,
            self.state.velocity.y,
            self.state.velocity.z,
        ])
        # The lateral axis is to the agent's starboard.
        lateral = np.array([roll[1], -roll[0], 0])
        # The yaw axis points upwards relative to the agent's roll-lateral plane.
        yaw = np.cross(lateral, roll)
        return roll, lateral, yaw

    def get_normalized_principal_axes(
            self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Returns the normalized_principal axes of the agent.

        Returns:
            A 3-tuple consisting of the normalized roll, lateral, and yaw axes.
        """
        roll, lateral, yaw = self.get_principal_axes()
        normalized_roll = roll / np.linalg.norm(roll)
        normalized_lateral = lateral / np.linalg.norm(lateral)
        normalized_yaw = yaw / np.linalg.norm(yaw)
        return normalized_roll, normalized_lateral, normalized_yaw

    def get_gravity(self) -> np.ndarray:
        """Returns the gravity acceleration vector."""
        gravity = np.array([
            0,
            0,
            -constants.gravity_at_altitude(self.state.position.z),
        ])
        return gravity

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
            if position_z <= 0:
                dx = np.zeros(state.shape)
            else:
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


class StaticAgent(Agent):
    """Static agent.

    A static agent maintains its initial state and does not update its state
    according to its environment.
    """

    def __init__(self, initial_state: State) -> None:
        super().__init__(initial_state)

    def update(self) -> None:
        """Updates the agent's state according to the environment."""
        return
