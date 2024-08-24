"""The plotter plots the trajectories of the missiles and the targets."""

import matplotlib.pyplot as plt
import scienceplots
from matplotlib import animation, artist

from simulation.swarm.agent import Agent
from simulation.swarm.missile import Missile
from simulation.swarm.target import Target


class Plotter:
    """Plotter for the agent trajectories.

    Attributes:
        missiles: List of missiles for which to plot the trajectory.
        targets: List of targets for which to plot the trajectory.
    """

    def __init__(self, missiles: list[Missile], targets: list[Target]) -> None:
        self.missiles = missiles
        self.targets = targets

    def plot(self) -> None:
        """Plots the trajectories of the missiles and the targets."""
        plt.style.use("science")
        fig, ax = plt.subplots(
            figsize=(12, 8),
            subplot_kw={"projection": "3d"},
        )
        ax.set_xlabel(r"$x$ [m]")
        ax.set_ylabel(r"$y$ [m]")
        ax.set_zlabel(r"$z$ [m]")
        ax.set_title("Agent trajectories")

        missile_trajectories = [(ax.plot(*self._get_positions(missile),
                                         color="blue",
                                         marker="^",
                                         markevery=[-1])[0])
                                for missile in self.missiles]
        target_trajectories = [(ax.plot(*self._get_positions(target),
                                        color="red",
                                        marker="s",
                                        markevery=[-1])[0])
                               for target in self.targets]
        num_time_steps = max([
            *[len(missile.history) for missile in self.missiles],
            *[len(target.history) for target in self.targets]
        ])

        def update_trajectories(frame: int) -> tuple[artist.Artist, ...]:
            """Updates the trajectories.

            Args:
                frame: Frame number.

            Returns:
                An iterable of artists.
            """
            max_index = frame % num_time_steps
            for missile_index, missile in enumerate(self.missiles):
                x, y, z = self._get_positions(missile, max_index)
                missile_trajectories[missile_index].set_data(x, y)
                missile_trajectories[missile_index].set_3d_properties(z)
            for target_index, target in enumerate(self.targets):
                x, y, z = self._get_positions(target, max_index)
                target_trajectories[target_index].set_data(x, y)
                target_trajectories[target_index].set_3d_properties(z)
            return *missile_trajectories, *target_trajectories

        anim = animation.FuncAnimation(
            fig,
            update_trajectories,
            interval=1,
            blit=True,
            cache_frame_data=False,
        )
        plt.show()

    @staticmethod
    def _get_positions(
            agent: Agent,
            max_index: int = -1
    ) -> tuple[list[float], list[float], list[float]]:
        """Returns the positions of the agent up to the given maximum index.

        Args:
            agent: Agent.
            max_index: Maximum index to return. If -1, return all time steps.

        Returns:
            A 3-tuple consisting of the agent's x, y, and z positions.
        """
        x = [state.position.x for _, state in agent.history[:max_index]]
        y = [state.position.y for _, state in agent.history[:max_index]]
        z = [state.position.z for _, state in agent.history[:max_index]]
        return x, y, z
