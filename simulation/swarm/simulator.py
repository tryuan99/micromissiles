"""The simulator class defines all agents and runs the simulation."""

import numpy as np
from absl import logging

from simulation.swarm.missiles.missile import MISSILE_TYPE_ENUM_TO_CLASS
from simulation.swarm.plotter import Plotter
from simulation.swarm.proto.simulator_config_pb2 import SimulatorConfig
from simulation.swarm.targets.target import TARGET_TYPE_ENUM_TO_CLASS
from simulation.swarm.targets.target_assignment import \
    DistanceBasedTargetAssignment


class Simulator:
    """Simulator.

    Attributes:
        t_step: Simulation step time in seconds.
        missiles: List of missiles.
        targets: List of targets.
    """

    def __init__(self, simulator_config: SimulatorConfig) -> None:
        self.t_step = simulator_config.step_time
        self.missiles = [
            MISSILE_TYPE_ENUM_TO_CLASS[missile_config.type](missile_config)
            for missile_config in simulator_config.missile_configs
        ]
        self.targets = [
            TARGET_TYPE_ENUM_TO_CLASS[target_config.type](target_config)
            for target_config in simulator_config.target_configs
        ]

    def run(self, t_end: float) -> None:
        """Runs the simulation for the given time span in increments of the
        given step time.

        Args:
            t_end: Time span in seconds.
        """
        # Step through the simulation.
        for t in np.arange(0, t_end, self.t_step):
            logging.log_every_n(logging.INFO, "Simulating time t=%f.", 1000, t)

            # Assign the targets to the missiles.
            target_assignment = DistanceBasedTargetAssignment(
                self.missiles, self.targets)
            for (missile_index, target_index
                ) in target_assignment.missile_to_target_assignments.items():
                self.missiles[missile_index].assign_target(
                    self.targets[target_index])

            # Update the acceleration vectors of each agent.
            for agent in [*self.missiles, *self.targets]:
                if not agent.hit:
                    agent.update(t)

            # Step to the next time step.
            for agent in [*self.missiles, *self.targets]:
                if not agent.hit:
                    agent.step(t, self.t_step)

    def plot(self, animate: bool, animation_file: str) -> None:
        """Plots the agent trajectories over time.

        Args:
            animate: If true, animate the trajectories.
            animation_file: Animation file.
        """
        agents = [*self.missiles, *self.targets]
        plotter = Plotter(self.t_step, agents)
        plotter.plot(animate, animation_file)
