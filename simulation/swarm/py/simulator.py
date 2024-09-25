"""The simulator class defines all agents and runs the simulation."""

import numpy as np
from absl import logging
from simulation.swarm.proto.simulator_config_pb2 import SimulatorConfig

from simulation.swarm.assignment.py.distance_assignment import \
    DistanceAssignment
from simulation.swarm.interceptor.py.interceptor import \
    INTERCEPTOR_TYPE_ENUM_TO_CLASS
from simulation.swarm.plotter.py.plotter import Plotter
from simulation.swarm.threat.py.threat import THREAT_TYPE_ENUM_TO_CLASS


class Simulator:
    """Simulator.

    Attributes:
        t_step: Simulation step time in seconds.
        interceptors: List of interceptors.
        threats: List of threats.
    """

    def __init__(self, simulator_config: SimulatorConfig) -> None:
        self.t_step = simulator_config.step_time
        self.interceptors = [
            INTERCEPTOR_TYPE_ENUM_TO_CLASS[interceptor_config.interceptor_type](
                interceptor_config, ready=False)
            for interceptor_config in simulator_config.interceptor_configs
        ]
        self.threats = [
            THREAT_TYPE_ENUM_TO_CLASS[threat_config.threat_type](threat_config,
                                                                 ready=False)
            for threat_config in simulator_config.threat_configs
        ]

    def run(self, t_end: float) -> None:
        """Runs the simulation for the given time span.

        Args:
            t_end: Time span in seconds.
        """
        # Step through the simulation.
        for t in np.arange(0, t_end, self.t_step):
            logging.log_every_n(logging.INFO, "Simulating time t=%f.", 1000, t)

            # Have all interceptors check their threats.
            for interceptor in self.interceptors:
                interceptor.check_threat()

            # Allow agents to spawn new instances.
            spawned_interceptors = []
            spawned_threats = []
            for interceptor in self.interceptors:
                spawned_interceptors.extend(interceptor.spawn(t))
            for threat in self.threats:
                spawned_threats.extend(threat.spawn(t))
            self.interceptors.extend(spawned_interceptors)
            self.threats.extend(spawned_threats)

            # Assign the threats to the interceptors.
            threat_assignment = DistanceAssignment(self.interceptors,
                                                   self.threats)
            for (
                    interceptor_index, threat_index
            ) in threat_assignment.interceptor_to_threat_assignments.items():
                self.interceptors[interceptor_index].assign_threat(
                    self.threats[threat_index])

            # Update the acceleration vector of each agent.
            for agent in [*self.interceptors, *self.threats]:
                if not agent.has_terminated():
                    agent.update(t)

            # Step to the next time step.
            for agent in [*self.interceptors, *self.threats]:
                if agent.has_launched() and not agent.has_terminated():
                    agent.step(t, self.t_step)

    def plot(self, animate: bool, animation_file: str) -> None:
        """Plots the agent trajectories over time.

        Args:
            animate: If true, animate the trajectories.
            animation_file: Animation file.
        """
        agents = [*self.interceptors, *self.threats]
        plotter = Plotter(self.t_step, agents)
        plotter.plot(animate, animation_file)
