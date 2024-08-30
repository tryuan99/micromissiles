"""The simulator class defines all agents and runs the simulation."""

import numpy as np
from absl import logging

from simulation.swarm.missile import Missile
from simulation.swarm.plotter import Plotter
from simulation.swarm.proto.simulator_config_pb2 import SimulatorConfig
from simulation.swarm.target import Target


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
            Missile(missile_config)
            for missile_config in simulator_config.missile_configs
        ]
        self.targets = [
            Target(target_config)
            for target_config in simulator_config.target_configs
        ]

    def run(self, t_end: float) -> None:
        """Runs the simulation for the given time span in increments of the
        given step time.

        Args:
            t_end: Time span in seconds.
        """
        # Assign the targets to the missiles.
        # TODO(titan): Implement some optimal matching algorithm.
        for missile_index, missile in enumerate(self.missiles):
            target_index = missile_index % len(self.targets)
            missile.assign_target(self.targets[target_index])

        # Step through the simulation.
        for t in np.arange(0, t_end, self.t_step):
            logging.log_every_n(logging.INFO, "Simulating time t=%f.", 1000, t)
            for agent in [*self.missiles, *self.targets]:
                if not agent.hit:
                    agent.update(t)
            for agent in [*self.missiles, *self.targets]:
                if not agent.hit:
                    agent.step(t, self.t_step)

    def plot(self, animate: bool, animation_file: str) -> None:
        """Plots the agent trajectories over time.

        Args:
            animate: If true, animate the trajectories.
            animation_file: Animation file.
        """
        plotter = Plotter(self.t_step, self.missiles, self.targets)
        plotter.plot(animate, animation_file)
