"""The plotter plots the trajectories of the agents."""

import matplotlib.pyplot as plt
import numpy as np
import scienceplots
from matplotlib import animation, artist

from simulation.swarm.agent import Agent
from simulation.swarm.proto.plotting_config_pb2 import Color, LineStyle, Marker

# Animation interval in fps.
PLOTTER_ANIMATION_FPS = 50

# Map from the color enumeration to the color string.
COLOR_ENUM_TO_STRING = {
    Color.BLACK: "black",
    Color.BLUE: "blue",
    Color.ORANGE: "orange",
    Color.GREEN: "green",
    Color.RED: "red",
    Color.PURPLE: "purple",
    Color.BROWN: "brown",
    Color.PINK: "pink",
    Color.GRAY: "gray",
    Color.OLIVE: "olive",
    Color.CYAN: "cyan",
}

# Map from the line style enumeration to the line style string.
LINE_STYLE_ENUM_TO_STRING = {
    LineStyle.SOLID: "solid",
    LineStyle.DOTTED: "dotted",
    LineStyle.DASHED: "dashed",
    LineStyle.DASHDOT: "dashdot",
}

# Map from the marker enumeration to the marker string.
MARKER_ENUM_TO_STRING = {
    Marker.NONE: "",
    Marker.CIRCLE: "o",
    Marker.TRIANGLE_DOWN: "v",
    Marker.TRIANGLE_UP: "^",
    Marker.TRIANGLE_LEFT: "<",
    Marker.TRIANGLE_RIGHT: ">",
    Marker.OCTAGON: "8",
    Marker.SQUARE: "s",
    Marker.PENTAGON: "p",
    Marker.PLUS: "P",
    Marker.STAR: "*",
    Marker.HEXAGON: "h",
    Marker.X: "X",
    Marker.DIAMOND: "D",
    Marker.THIN_DIAMOND: "d",
}


class Plotter:
    """Plotter for the agent trajectories.

    Attributes:
        t_step: Simulation step time in seconds.
        agents: List of agents for which to plot the trajectory.
    """

    def __init__(self, t_step: float, agents: list[Agent]) -> None:
        self.t_step = t_step
        self.agents = agents

    def plot(self, animate: bool = True, animation_file: str = None) -> None:
        """Plots the trajectories of the agents.

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

        def plot_agent_trajectory(agent: Agent) -> artist.Artist:
            """Plots the trajectory of the agent.

            Args:
                agent: Agent for which to plot the trajectory.

            Returns:
                An artist corresponding to the trajectory.
            """
            color = COLOR_ENUM_TO_STRING[agent.plotting_config.color]
            linestyle = (
                LINE_STYLE_ENUM_TO_STRING[agent.plotting_config.linestyle])
            marker = MARKER_ENUM_TO_STRING[agent.plotting_config.marker]
            artist = ax.plot(
                *self._get_positions(agent),
                color=color,
                linestyle=linestyle,
                marker=marker,
                markevery=[-1],
            )[0]
            return artist

        agent_trajectories = [
            plot_agent_trajectory(agent) for agent in self.agents
        ]
        num_time_steps = max([len(agent.history) for agent in self.agents])

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
            for agent_index, agent in enumerate(self.agents):
                x, y, z = self._get_positions(agent, frame)
                agent_trajectories[agent_index].set_data(x, y)
                agent_trajectories[agent_index].set_3d_properties(z)
            return agent_trajectories

        # Animate at a frame rate of at most 50 fps.
        num_steps_per_frame = int(
            np.ceil(1 / (PLOTTER_ANIMATION_FPS * self.t_step)))
        effective_fps = 1 / (num_steps_per_frame * self.t_step)
        anim = animation.FuncAnimation(
            fig,
            update_trajectories,
            frames=np.arange(0, num_time_steps, num_steps_per_frame),
            interval=1000 / effective_fps,
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
