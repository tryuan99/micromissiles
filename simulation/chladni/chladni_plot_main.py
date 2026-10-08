"""Plots the amplitude and phase of a driven Chladni plate."""

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from absl import app, flags

import utils.visualization.mpl_config
from utils.visualization.color_maps import COLOR_MAPS

FLAGS = flags.FLAGS


class ResponsePlotter:
    """Plots the amplitude and phase written by chladni_main.

    The CSV file only contains points on the plate, so the points are placed
    back onto the full grid with NaN off the plate.

    Attributes:
        x: x-coordinates of the grid in m.
        y: y-coordinates of the grid in m.
        amplitude: Amplitude in m.
        phase: Phase in rad.
    """

    def __init__(self, df: pd.DataFrame) -> None:
        (
            x_column,
            y_column,
            amplitude_column,
            phase_column,
        ) = df.columns
        x = df[x_column].to_numpy()
        y = df[y_column].to_numpy()
        amplitude = df[amplitude_column].to_numpy()
        phase = df[phase_column].to_numpy()

        x_values, x_indices = np.unique(x, return_inverse=True)
        y_values, y_indices = np.unique(y, return_inverse=True)

        self.x, self.y = np.meshgrid(x_values, y_values, indexing="ij")
        self.amplitude = np.full((len(x_values), len(y_values)), np.nan)
        self.amplitude[x_indices, y_indices] = amplitude
        self.phase = np.full((len(x_values), len(y_values)), np.nan)
        self.phase[x_indices, y_indices] = phase

    def plot_amplitude(self, nodes: bool) -> None:
        """Plots the amplitude in m.

        Args:
            nodes: If true, draws the nodes as dashed lines.
        """
        self._plot(
            self.amplitude,
            COLOR_MAPS["parula"],
            "Amplitude [m]",
            nodes,
            "white",
        )

    def plot_phase(self, nodes: bool) -> None:
        """Plots the phase in rad.

        Args:
            nodes: If true, draws the nodes as dashed lines.
        """
        self._plot(
            self.phase,
            "twilight",
            "Phase [rad]",
            nodes,
            "cyan",
            (-np.pi, np.pi),
        )

    def _plot(
        self,
        values: np.ndarray,
        colormap: str | matplotlib.colors.Colormap,
        label: str,
        nodes: bool,
        node_color: str,
        min_value=None,
        max_value=None,
    ) -> None:
        """Plots the values.

        Args:
            values: Values to plot.
            colormap: Colormap.
            label: Label of the color bar.
            nodes: If true, draws the nodes as dashed lines.
            node_color: Color of the node lines.
            min_value: Minimum value.
            max_value: Maximum value.
        """
        fig, ax = plt.subplots(figsize=(6, 6))
        mesh = ax.pcolormesh(
            self.x,
            self.y,
            values,
            cmap=colormap,
            vmin=min_value,
            vmax=max_value,
            shading="nearest",
        )
        if nodes:
            ax.contour(
                self.x,
                self.y,
                self._real_response(),
                [0],
                colors=node_color,
                linestyles="--",
            )
        fig.colorbar(mesh, ax=ax, label=label)
        ax.set_aspect("equal")
        ax.set_xlabel("x [m]")
        ax.set_ylabel("y [m]")
        ax.grid(False)
        plt.show()

    def _real_response(self) -> np.ndarray:
        """Returns the signed amplitude response after removing the overall
        phase of the response.

        The nodes are where the real part is zero.
        """
        response = self.amplitude * np.exp(1j * self.phase)
        phase = 0.5 * np.angle(np.nansum(response**2))
        return np.real(response * np.exp(-1j * phase))


def main(argv):
    assert len(argv) == 1

    df = pd.read_csv(FLAGS.response_csv, comment="#")
    plotter = ResponsePlotter(df)
    plotter.plot_amplitude(FLAGS.nodes)
    plt.show()


if __name__ == "__main__":
    flags.DEFINE_string("response_csv", None,
                        "CSV file written by chladni_main.")
    flags.DEFINE_bool("nodes", False, "Draw the nodes as dashed lines.")
    flags.mark_flag_as_required("response_csv")

    app.run(main)
