"""The agent class is an interface for a missile or a target."""

from abc import ABC, abstractmethod

import numpy as np
import scipy.integrate

from simulation.swarm import constants
from simulation.swarm.proto.missile_config_pb2 import MissileConfig
from simulation.swarm.proto.physical_config_pb2 import PhysicalConfig
from simulation.swarm.proto.plotting_config_pb2 import PlottingConfig
from simulation.swarm.proto.state_pb2 import State
from simulation.swarm.proto.target_config_pb2 import TargetConfig


class Agent(ABC):
    """Agent.

    Attributes:
        state: The current state.
        physical_config: The physical configuration of the agent.
        plotting_config: The plotting configuration of the agent.
        history: A list of 2-tuples consisting of a timestamp and the state.
        hit: A boolean indicating whether the agent has hit or been hit.
        update_time: The time of the last state update.
    """

    def __init__(
        self,
        config: MissileConfig | TargetConfig = None,
        *,
        initial_state: State = None,
        physical_config: PhysicalConfig = None,
        plotting_config: PlottingConfig = None,
    ) -> None:
        # Set the initial state.
        self.state = State()
        if initial_state is not None:
            self.state.CopyFrom(initial_state)
        else:
            self.state.CopyFrom(config.initial_state)

        # Set the physical configuration.
        self.physical_config = PhysicalConfig()
        if physical_config is not None:
            self.physical_config.CopyFrom(physical_config)
        elif config is not None:
            self.physical_config.CopyFrom(config.physical_config)

        # Set the plotting configuration.
        self.plotting_config = PlottingConfig()
        if plotting_config is not None:
            self.plotting_config.CopyFrom(plotting_config)
        elif config is not None:
            self.plotting_config.CopyFrom(config.plotting_config)

        self.hit = False
        self.history = [(0, State())]
        self.history[-1][1].CopyFrom(self.state)
        self.update_time = 0

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
        roll = self.get_velocity()
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

    def get_position(self) -> np.ndarray:
        """Returns the position vector of the agent."""
        position = np.array([
            self.state.position.x,
            self.state.position.y,
            self.state.position.z,
        ])
        return position

    def get_velocity(self) -> np.ndarray:
        """Returns the velocity vector of the agent."""
        velocity = np.array([
            self.state.velocity.x,
            self.state.velocity.y,
            self.state.velocity.z,
        ])
        return velocity

    def get_speed(self) -> float:
        """Returns the speed of the agent."""
        velocity = self.get_velocity()
        speed = np.linalg.norm(velocity)
        return speed

    def get_gravity(self) -> np.ndarray:
        """Returns the gravity acceleration vector."""
        gravity = np.array([
            0,
            0,
            -constants.gravity_at_altitude(self.state.position.z),
        ])
        return gravity

    def get_dynamic_pressure(self) -> float:
        """Calculates the dynamic air pressure around the agent."""
        air_density = constants.air_density_at_altitude(self.state.position.z)
        flow_speed = self.get_speed()
        dynamic_pressure = 1 / 2 * air_density * flow_speed**2
        return dynamic_pressure

    @abstractmethod
    def update(self, t: float) -> None:
        """Updates the agent's state according to the environment.

        Args:
            t: Time in seconds.
        """

    def set_state(self, state: State) -> None:
        """Sets the state of the agent."""
        self.state.CopyFrom(state)
        # Update the latest state in the history of states.
        self.history[-1][1].CopyFrom(state)

    def step(self, t_start: float, t_step: float) -> None:
        """Steps forward the simulation by simulating the dynamics of the
        agent.

        This function mutates the agent's state variable.
        TODO(titan): Evolve the agent's roll, pitch, and yaw.

        Args:
            t_start: Start time in seconds.
            t_step: Step time in seconds.
        """
        # Update the latest state in the history of states.
        self.history[-1][1].CopyFrom(self.state)

        # Check if the step time is zero.
        if t_step == 0:
            return

        position = self.get_position()
        velocity = self.get_velocity()
        initial_state = np.concatenate((position, velocity))

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
        t = t_start + t_step
        self.history.append((t, State()))
        self.history[-1][1].CopyFrom(self.state)
        self.update_time = t


class ModelAgent(Agent):
    """Model agent.

    A model agent models an agent without any physical configuration.
    """

    def __init__(
        self,
        initial_state: State,
    ) -> None:
        super().__init__(initial_state=initial_state)

    def update(self, t: float) -> None:
        """Updates the agent's state according to the environment.

        Args:
            t: Time in seconds.
        """
        return
