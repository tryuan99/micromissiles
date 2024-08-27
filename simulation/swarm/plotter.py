"""The plotter plots the trajectories of the missiles and the targets."""

import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from matplotlib import animation, artist

from simulation.swarm.agent import Agent
from simulation.swarm.missile import Missile
from simulation.swarm.target import Target

# Animation interval in fps.
PLOTTER_ANIMATION_FPS = 50

# Animation speed factor.
PLOTTER_ANIMATION_SPEED_FACTOR = 0.1


class Plotter:
    """Plotter for the agent trajectories.

    Attributes:
        t_step: Simulation step time in seconds.
        missiles: List of missiles for which to plot the trajectory.
        targets: List of targets for which to plot the trajectory.
    """

    def __init__(self, t_step: float, missiles: list[Missile],
                 targets: list[Target]) -> None:
        self.t_step = t_step
        self.missiles = missiles
        self.targets = targets

    def plot(self, animate: bool = True, animation_file: str = None) -> None:
        """Plots the trajectories of the missiles and the targets.

        Args:
            animation_file: Animation file.
        """
        plt.style.use("science")
        fig, ax = plt.subplots(
            figsize=(6, 6),
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
            *[len(target.history) for target in self.targets],
        ])

        # Plot the trajectories if no animation is required.
        if not animate:
            plt.show()
            return

        def update_trajectories(frame: int) -> tuple[artist.Artist, ...]:
            """Updates the trajectories.

            Args:
                frame: Frame number.

            Returns:
                An iterable of artists.
            """
            for missile_index, missile in enumerate(self.missiles):
                x, y, z = self._get_positions(missile, frame)
                missile_trajectories[missile_index].set_data(x, y)
                missile_trajectories[missile_index].set_3d_properties(z)
            for target_index, target in enumerate(self.targets):
                x, y, z = self._get_positions(target, frame)
                target_trajectories[target_index].set_data(x, y)
                target_trajectories[target_index].set_3d_properties(z)
            return *missile_trajectories, *target_trajectories

        # Animate at a frame rate of at most 50 fps.
        num_steps_per_frame = int(
            np.ceil(PLOTTER_ANIMATION_SPEED_FACTOR /
                    (PLOTTER_ANIMATION_FPS * self.t_step)))
        effective_fps = (PLOTTER_ANIMATION_SPEED_FACTOR /
                         (num_steps_per_frame * self.t_step))
        anim = animation.FuncAnimation(
            fig,
            update_trajectories,
            frames=np.arange(0, num_time_steps, num_steps_per_frame),
            interval=1 / effective_fps,
            blit=True,
            cache_frame_data=False,
        )
        # Save the animation.
        if animation_file is not None:
            anim.save(
                filename=animation_file,
                writer="ffmpeg",
                fps=effective_fps,
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
