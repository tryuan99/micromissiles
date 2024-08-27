"""The simulator class defines all agents and runs the simulation."""

import numpy as np

from simulation.swarm.missile import Missile
from simulation.swarm.plotter import Plotter
from simulation.swarm.proto.simulator_config_pb2 import SimulatorConfig
from simulation.swarm.target import Target


class Simulator:
    """Simulator.

    Attributes:
        missiles: List of missiles.
        targets: List of targets.
    """

    def __init__(self, simulator_config: SimulatorConfig) -> None:
        self.missiles = [
            Missile(missile_config)
            for missile_config in simulator_config.missile_configs
        ]
        self.targets = [
            Target(target_config)
            for target_config in simulator_config.target_configs
        ]

    def run(self, t_end: float, t_step: float) -> None:
        """Runs the simulation for the given time span in increments of the
        given step time.

        Args:
            t_end: Time span in seconds.
            t_step: Step time in seconds.
        """
        # Assign the targets to the missiles.
        # TODO(titan): Implement some optimal matching algorithm.
        for missile_index, missile in enumerate(self.missiles):
            target_index = missile_index % len(self.targets)
            missile.assign(self.targets[target_index])

        # Step through the simulation.
        for t in np.arange(0, t_end, t_step):
            for agent in [*self.missiles, *self.targets]:
                agent.update()
            for agent in [*self.missiles, *self.targets]:
                agent.step(t, t_step)

    def plot(self) -> None:
        """Plots the agent trajectories over time."""
        plotter = Plotter(self.missiles, self.targets)
        plotter.plot()
