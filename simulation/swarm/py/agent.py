"""The agent class is an interface for an interceptor or a threat."""

from abc import ABC, abstractmethod
from collections import namedtuple
from typing import Self

import numpy as np
import scipy.integrate
from simulation.swarm.proto.agent_pb2 import AgentConfig, FlightPhase
from simulation.swarm.proto.dynamic_config_pb2 import DynamicConfig
from simulation.swarm.proto.plotting_config_pb2 import PlottingConfig
from simulation.swarm.proto.state_pb2 import State
from simulation.swarm.proto.static_config_pb2 import StaticConfig

from simulation.swarm.utils.py import constants


class Agent(ABC):
    """Agent.

    Attributes:
        t_creation: The agent's creation time in s.
        state: The current state.
        state_update_time: The time of the last state update in s.
        flight_phase: The flight phase of the agent.
        static_config: The static configuration of the agent.
        dynamic_config: The dynamic configuration of the agent.
        plotting_config: The plotting configuration of the agent.
        submunitions_config: The submunitions configuration of the agent.
        history: A list of 3-tuples consisting of a timestamp, the hit boolean,
          and the state.
        hit: A boolean indicating whether the agent has hit or been hit.
    """

    # History record named tuple type.
    HistoryRecord = namedtuple("HistoryRecord", ["t", "hit", "state"])

    def __init__(
        self,
        config: AgentConfig = None,
        ready: bool = True,
        t_creation: float = 0,
        *,
        initial_state: State = None,
        dynamic_config: DynamicConfig = None,
        plotting_config: PlottingConfig = None,
        submunitions_config: AgentConfig.SubmunitionsConfig = None,
    ) -> None:
        self.t_creation = t_creation

        # Set the initial state.
        self.state = State()
        if initial_state is not None:
            self.state.CopyFrom(initial_state)
        else:
            self.state.CopyFrom(config.initial_state)
        self.state_update_time = 0
        # In the initialized flight phase, the agent idles, but in the ready
        # flight phase, the agent is subject to physical forces.
        self.flight_phase = (FlightPhase.READY
                             if ready else FlightPhase.INITIALIZED)

        # Set the dynamic configuration.
        self.dynamic_config = DynamicConfig()
        if dynamic_config is not None:
            self.dynamic_config.CopyFrom(dynamic_config)
        elif config is not None:
            self.dynamic_config.CopyFrom(config.dynamic_config)

        # Set the plotting configuration.
        self.plotting_config = PlottingConfig()
        if plotting_config is not None:
            self.plotting_config.CopyFrom(plotting_config)
        elif config is not None:
            self.plotting_config.CopyFrom(config.plotting_config)

        # Set the submunitions configuration.
        self.submunitions_config = AgentConfig.SubmunitionsConfig()
        if submunitions_config is not None:
            self.submunitions_config.CopyFrom(submunitions_config)
        elif config is not None:
            self.submunitions_config.CopyFrom(config.submunitions_config)

        self.hit = False
        self.history = [
            Agent.HistoryRecord(t=self.t_creation, hit=self.hit, state=State())
        ]
        self.history[-1].state.CopyFrom(self.state)

    @property
    @abstractmethod
    def static_config(self) -> StaticConfig:
        """Returns the static configuration of the agent."""

    def has_launched(self) -> bool:
        """Returns whether the agent has launched."""
        return (self.flight_phase != FlightPhase.INITIALIZED and
                self.flight_phase != FlightPhase.READY)

    def has_terminated(self) -> bool:
        """Returns whether the agent's flight has terminated."""
        return self.flight_phase == FlightPhase.TERMINATED

    def mark_as_hit(self) -> None:
        """Sets the agent to have hit the target or have been hit."""
        self.hit = True
        # Update the latest hit boolean in the history of states.
        self.history[-1] = self.history[-1]._replace(hit=True)
        self.flight_phase = FlightPhase.TERMINATED

    def set_state(self, state: State) -> None:
        """Sets the state of the agent."""
        self.state.CopyFrom(state)
        # Update the latest state in the history of states.
        self.history[-1].state.CopyFrom(state)

    def get_principal_axes(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Returns the principal axes of the agent.

        The principal axis directions have not been normalized.
        The roll axis is assumed to be aligned with the agent's velocity vector,
        and the pitch axis points to the starboard of the agent.
        TODO(titan): The roll axis does not necessarily have to be aligned with
        the agent's velocity vector.

        Returns:
            A 3-tuple consisting of the roll, pitch, and yaw axes.
        """
        # The roll axis is assumed to be aligned with the agent's velocity
        # vector.
        roll = self.get_velocity()
        # The pitch axis is to the agent's starboard.
        pitch = np.array([roll[1], -roll[0], 0])
        # The yaw axis points upwards relative to the agent's roll-pitch plane.
        yaw = np.cross(pitch, roll)
        return roll, pitch, yaw

    def get_normalized_principal_axes(
            self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Returns the normalized_principal axes of the agent.

        Returns:
            A 3-tuple consisting of the normalized roll, pitch, and yaw axes.
        """
        roll, pitch, yaw = self.get_principal_axes()
        normalized_roll = roll / np.linalg.norm(roll)
        normalized_pitch = pitch / np.linalg.norm(pitch)
        normalized_yaw = yaw / np.linalg.norm(yaw)
        return normalized_roll, normalized_pitch, normalized_yaw

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

    def update(self, t: float) -> None:
        """Updates the agent's state according to the environment.

        Args:
            t: Time in seconds.
        """
        launch_time = self.dynamic_config.launch_config.launch_time
        boost_time = self.static_config.boost_config.boost_time

        # Determine the flight phase.
        if t >= self.t_creation + launch_time:
            self.flight_phase = FlightPhase.BOOST
        if t >= self.t_creation + launch_time + boost_time:
            self.flight_phase = FlightPhase.MIDCOURSE
        # TODO(titan): Determine when to enter the terminal phase.

        match self.flight_phase:
            case FlightPhase.INITIALIZED:
                return
            case FlightPhase.READY:
                self._update_ready(t)
            case FlightPhase.BOOST:
                self._update_boost(t)
            case FlightPhase.MIDCOURSE | FlightPhase.TERMINAL:
                self._update(t)
            case FlightPhase.TERMINATED:
                return
            case _:
                raise ValueError(f"Invalid flight phase: {self.flight_phase}.")

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
        self.history[-1] = self.history[-1]._replace(t=t_start)
        self.history[-1].state.CopyFrom(self.state)

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
            if position_z < 0:
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
        self.history.append(
            Agent.HistoryRecord(t=t, hit=self.hit, state=State()))
        self.history[-1].state.CopyFrom(self.state)
        self.state_update_time = t

    def spawn(self, t: float) -> list[Self]:
        """Spawns new agents.

        Args:
            t: Time in seconds.

        Returns:
            A list of newly spawned agents.
        """
        return []

    def _update_ready(self, t: float) -> None:
        """Updates the agent's state in the ready flight phase.

        Args:
            t: Time in seconds.
        """
        # By default, idle in the ready flight phase.
        return

    def _update_boost(self, t: float) -> None:
        """Updates the agent's state in the boost flight phase.

        Args:
            t: Time in seconds.
        """
        # By default, idle in the boost flight phase.
        return

    def _update(self, t: float) -> None:
        """Updates the agent's state in the midcourse and terminal flight
        phase.

        Args:
            t: Time in seconds.
        """
        # By default, idle in the midcourse and terminal flight phase.
        return
