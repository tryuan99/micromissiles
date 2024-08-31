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
        num_time_steps: Number of time steps to plot.
        agents: List of agents for which to plot the trajectory.
    """

    def __init__(self, t_step: float, agents: list[Agent]) -> None:
        self.t_step = t_step
        self.num_time_steps = int(
            max([agent.history[-1].t for agent in agents]) / self.t_step)
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
                An artist corresponding to the trajectory of the agent.
            """
            color = COLOR_ENUM_TO_STRING[agent.plotting_config.color]
            linestyle = (
                LINE_STYLE_ENUM_TO_STRING[agent.plotting_config.linestyle])
            marker = (MARKER_ENUM_TO_STRING[Marker.STAR]
                      if agent.history[-1].hit else
                      MARKER_ENUM_TO_STRING[agent.plotting_config.marker])
            artist = ax.plot(
                *self._get_positions(agent, self.num_time_steps),
                color=color,
                linestyle=linestyle,
                marker=marker,
                markevery=[-1],
            )[0]
            return artist

        # Plot the agent trajectories.
        agent_trajectories = [
            plot_agent_trajectory(agent) for agent in self.agents
        ]

        # Plot the trajectories if no animation is required.
        if not animate:
            plt.show()
            return

        def update_agent_trajectories(frame: int) -> tuple[artist.Artist, ...]:
            """Updates the trajectories of the agents.

            Args:
                frame: Frame number.

            Returns:
                An iterable of artists.
            """
            for agent_index, agent in enumerate(self.agents):
                x, y, z = self._get_positions(agent, frame)
                agent_trajectories[agent_index].set_data(x, y)
                agent_trajectories[agent_index].set_3d_properties(z)

                # Set the marker.
                hit = self._get_hit(agent, frame)
                marker = (MARKER_ENUM_TO_STRING[Marker.STAR] if hit else
                          MARKER_ENUM_TO_STRING[agent.plotting_config.marker])
                agent_trajectories[agent_index].set_marker(marker)
            return agent_trajectories

        # Animate at a frame rate of at most 50 fps.
        num_steps_per_frame = int(
            np.ceil(1 / (PLOTTER_ANIMATION_FPS * self.t_step)))
        effective_fps = 1 / (num_steps_per_frame * self.t_step)
        anim = animation.FuncAnimation(
            fig,
            update_agent_trajectories,
            frames=np.arange(0, self.num_time_steps, num_steps_per_frame),
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

    def _get_positions(
        self,
        agent: Agent,
        frame: int,
    ) -> tuple[list[float], list[float], list[float]]:
        """Returns the positions of the agent up to the given frame.

        Args:
            agent: Agent.
            frame: Frame number.

        Returns:
            A 3-tuple consisting of the agent's x, y, and z positions.
        """
        max_index = self._frame_to_history_index(agent, frame) + 1
        if max_index <= 0:
            return [], [], []

        x = [record.state.position.x for record in agent.history[:max_index]]
        y = [record.state.position.y for record in agent.history[:max_index]]
        z = [record.state.position.z for record in agent.history[:max_index]]
        return x, y, z

    def _get_hit(self, agent: Agent, frame: int) -> bool:
        """Returns whether the agent has hit or been hit at the given frame.

        Args:
            agent: Agent.
            frame: Frame number.

        Returns:
            A boolean indicating whether the agent has hit or been hit.
        """
        index = self._frame_to_history_index(agent, frame)
        if index < 0:
            return False
        hit = agent.history[index].hit
        return hit

    def _frame_to_history_index(self, agent: Agent, frame: int) -> int:
        """Converts the given frame number to the index of the agent's history.

        Args:
            agent: Agent.
            frame: Frame number.

        Returns:
            The history index corresponding to the frame number.
        """
        t_history_start = agent.history[0].t
        frame_offset = int(t_history_start / self.t_step)
        index = frame - frame_offset
        return min(index, len(agent.history) - 1)
