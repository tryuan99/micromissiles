"""The animator class is an interface for 2D and 3D animations."""

from abc import ABC
from typing import Any, Callable, Iterable

import matplotlib.pyplot as plt
import scienceplots
from matplotlib import animation, artist, axes, cm


class Artist:
    """Artist.

    Attributes:
        artist: Trace to plot.
        update_artist: Callback functions to update the artist.
        label: Trace label.
    """

    def __init__(
        self,
        artist: artist.Artist,
        update_artist: Callable[[artist.Artist, Any], artist.Artist] = None,
        label: str = None,
    ) -> None:
        self.artist = artist
        self.update_artist = update_artist
        self.label = label

    def has_update(self) -> bool:
        """Returns whether the artist has an update function."""
        return self.update_artist is not None

    def has_label(self) -> bool:
        """Returns whether the artist has a label."""
        return self.label is not None


class Animator(ABC):
    """Animator interface.

    Attributes:
        ax: Matplotlib axes.
        frames: Data to pass to each animation frame.
        interval: Delay between frames in milliseconds.
        artists: List of artists.
        update_title: Callback function to update the title.
    """

    def __init__(self) -> None:
        self.ax: axes.Axes = None
        self.frames: Iterable = None
        self.interval = 200

        self.artists: list[Artist] = []
        self.update_title: Callable[[artist.Artist], None] = None

    def axes(self) -> axes.Axes:
        """Returns the axes."""
        return self.ax

    def add_artist(
        self,
        artist: artist.Artist,
        update_artist: Callable[[artist.Artist, Any], artist.Artist] = None,
        label: str = None,
    ) -> None:
        """Adds a trace to the animation.

        Args:
            artist: Trace to add.
            update_artist: Callback function to update the artist.
            label: Trace label.
        """
        self.ax.add_artist(artist)
        self.artists.append(Artist(artist, update_artist, label))

    def configure_animation(self, frames: Iterable, interval: float) -> None:
        """Configures the animation.

        Args:
            frames: Data to pass to each animation frame.
            interval: Delay between frames in milliseconds.
        """
        self.frames = frames
        self.interval = interval

    def set_title(
        self,
        title: str,
        update_title: Callable[[Any], None] = None,
    ) -> None:
        """Sets the title of the plot.

        Args:
            title: Plot title.
            update_title: Callback function to update the title.
        """
        self.ax.set_title(title)
        self.update_title = update_title

    def show(self, repeat: bool = True) -> None:
        """Shows the plot.

        Args:
            repeat: If true, repeats the animation after the sequence of frames
              is completed.
        """
        # Start the animation.
        anim = animation.FuncAnimation(
            self.fig,
            self._update_animation,
            frames=self.frames,
            interval=self.interval,
            repeat=repeat,
        )
        # Add a legend.
        artists_with_labels = [
            artist for artist in self.artists if artist.has_label()
        ]
        if len(artists_with_labels) > 0:
            self.ax.legend(
                [artist.artist for artist in artists_with_labels],
                [artist.label for artist in artists_with_labels],
            )
        plt.show()

    def _update_animation(self, frame: Any) -> None:
        """Update function to call at each frame.

        Args:
            frame: Frame data.
        """
        for artist in self.artists:
            if artist.has_update():
                artist.artist = artist.update_artist(artist.artist, frame)
        if self.update_title is not None:
            self.ax.set_title(self.update_title(frame))


class Animator2D(Animator):
    """2D animator.

    Attributes:
        fig: Matplotlib figure.
        ax: Matplotlib axes.
    """

    def __init__(self) -> None:
        super().__init__()
        plt.style.use(["science", "grid"])
        self.fig, self.ax = plt.subplots(figsize=(12, 6))

    def set_labels(self, xlabel: str, ylabel: str) -> None:
        """Sets the axis labels.

        Args:
            xlabel: x-axis label.
            ylabel: y-axis label.
        """
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)

    def set_limits(
            self,
            xlim: tuple[float, float] = (None, None),
            ylim: tuple[float, float] = (None, None),
    ) -> None:
        """Sets the axis limits.

        Args:
            xlim: x-axis limits.
            ylim: y-axis limits.
        """
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)


class Animator3D(Animator):
    """3D animator.

    Attributes:
        fig: Matplotlib figure.
        ax: Matplotlib axes.
    """

    def __init__(self) -> None:
        super().__init__()
        plt.style.use("science")
        self.fig, self.ax = plt.subplots(
            figsize=(12, 6),
            subplot_kw={"projection": "3d"},
        )

    def add_colorbar(self, m: cm.ScalarMappable) -> None:
        """Adds a colorbar to the plot.

        Args:
            m: Map from a scalar to a colormap.
        """
        plt.colorbar(m, ax=self.ax)

    def set_labels(self, xlabel: str, ylabel: str, zlabel: str) -> None:
        """Sets the axis labels.

        Args:
            xlabel: x-axis label.
            ylabel: y-axis label.
            zlabel: z-axis label.
        """
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        self.ax.set_zlabel(zlabel)

    def set_limits(
            self,
            xlim: tuple[float, float] = (None, None),
            ylim: tuple[float, float] = (None, None),
            zlim: tuple[float, float] = (None, None),
    ) -> None:
        """Sets the axis limits.

        Args:
            xlim: x-axis limits.
            ylim: y-axis limits.
            zlim: z-axis limits.
        """
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)
        self.ax.set_zlim(zlim)

    def view_init(
        self,
        elevation: float = None,
        azimuth: float = None,
        roll: float = None,
        vertical_axis: str = "z",
    ) -> None:
        """Sets the initial view.

        Args:
            elevation: Elevation angle in degrees.
            azimuth: Azimuth angle in degrees.
            roll: Roll angle in degrees.
            vertical_axis: Axis to align vertically.
        """
        self.ax.view_init(elevation, azimuth, roll, vertical_axis)
