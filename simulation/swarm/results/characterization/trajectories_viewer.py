"""The trajectories viewer processes and plots the simulated trajectories.

For an example of a trajectories CSV file containing the trajectories of a
Hydra-70 carrier interceptor with a micromissile interceptor, see one of the
following CSV files:
- https://drive.google.com/file/d/1_CWr8wQK_lumAY-2NtcY0-6_mn9DDOyl/view
- https://drive.google.com/file/d/1aR6F4_AAPiGW7UakczYtwo2uKZnvHT-W/view
- https://drive.google.com/file/d/13SbRva6yr3YIKUitowfXM6CCY_PapzRh/view
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import scienceplots
import scipy.interpolate
from absl import logging

from utils.visualization.color_maps import COLOR_MAPS, COLOR_MAPS_RGB


class TrajectoriesViewer:
    """Trajectories viewer.
    
    Attributes:
        df: Dataframe containing all trajectories.
        carrier_launch_angle_column: Carrier interceptor launch angle column.
        submunition_dispense_time_column: Submunition dispense time column.
        submunition_light_time_column: Submunition light time column.
        time_column: Time column.
        px_column: x-position column.
        py_column: y-position column.
        vx_column: x-velocity column.
        vy_column: y-velocity column.
        speed_column: Speed column.
    """

    def __init__(self, csv_file: str) -> None:
        # Read the trajectories CSV file.
        logging.info("Reading trajectories from CSV file: %s.", csv_file)
        self.df = pd.read_csv(csv_file, comment="#")
        (
            self.carrier_launch_angle_column,
            self.submunition_dispense_time_column,
            self.submunition_light_time_column,
            self.time_column,
            self.px_column,
            self.py_column,
            self.vx_column,
            self.vy_column,
        ) = self.df.columns

        # Add a column for the interceptor speed.
        self.speed_column = "Speed [m/s]"
        self.df[self.speed_column] = np.sqrt(
            np.square(self.df[[self.vx_column, self.vy_column]]).sum(axis=1))

        # Add a column for whether the carrier has dispensed its submunition.
        self.submunition_dispensed_column = "Dispensed"
        self.df[self.submunition_dispensed_column] = (
            self.df[self.time_column]
            > self.df[self.submunition_dispense_time_column])

        # Add a column whether the submunition has lighted.
        self.submunition_lighted_column = "Lighted"
        self.df[self.submunition_lighted_column] = (
            self.df[self.time_column]
            > (self.df[self.submunition_dispense_time_column] +
               self.df[self.submunition_light_time_column]))

        # Set the Matplotlib style.
        plt.style.use(["science", "grid"])

    def plot_all_trajectories(self) -> None:
        """Plots all trajectories."""
        fig, ax = plt.subplots(
            figsize=(12, 6),
            subplot_kw={"projection": "3d"},
        )
        scatter = ax.scatter(
            self.df[self.px_column],
            self.df[self.submunition_dispense_time_column],
            self.df[self.py_column],
            s=1,
            c=self.df[self.speed_column],
            cmap=COLOR_MAPS["parula"],
        )
        ax.set_xlabel("Position [m]")
        ax.set_ylabel("Submunition dispense time [s]")
        ax.set_zlabel("Altitude [m]")
        ax.set_title("Interceptor trajectories")
        plt.colorbar(scatter)
        plt.show()

    def plot_trajectories_with_dispense_time(
            self, submunition_dispense_time: float) -> None:
        """Plots all trajectories with the given submunition dispense time.
        
        Args:
            submunition_dispense_time: Submunition dispense time in seconds.
        """
        # Find all trajectories with the given submunition dispense time.
        df_with_submunition_dispense_time = (
            self.df[self.df[self.submunition_dispense_time_column] ==
                    submunition_dispense_time])

        # Plot the trajectories with the given submunition dispense time.
        fig, ax = plt.subplots(figsize=(12, 6))
        scatter = ax.scatter(
            df_with_submunition_dispense_time[self.px_column],
            df_with_submunition_dispense_time[self.py_column],
            s=1,
            c=df_with_submunition_dispense_time[self.speed_column],
            cmap=COLOR_MAPS["parula"],
        )
        ax.set_xlabel("Position [m]")
        ax.set_ylabel("Altitude [m]")
        ax.set_title(f"Interceptor trajectories with submunition dispense time "
                     rf"$t={submunition_dispense_time}$")
        plt.colorbar(scatter)
        plt.show()

    def plot_reachability_at_time(self, time: float) -> None:
        """Plots the trajectory points at the given time.
        
        Args:
            time: Time in seconds.
        """
        # Find all trajectory points at the given time.
        df_at_time = self.df[(self.df[self.time_column] == time)]

        # Plot the trajectory points in Matplotlib.
        fig, ax = plt.subplots(figsize=(12, 6))
        scatter = ax.scatter(
            df_at_time[self.px_column],
            df_at_time[self.py_column],
            s=3,
            c=df_at_time[self.speed_column],
            cmap=COLOR_MAPS["parula"],
        )
        ax.set_xlabel("Position [m]")
        ax.set_ylabel("Altitude [m]")
        ax.set_title(rf"Reachability at time $t={time}$")
        plt.colorbar(scatter)
        plt.show()

        # Plot the trajectory points in Plotly.
        fig = px.scatter(
            df_at_time,
            x=self.px_column,
            y=self.py_column,
            color=self.speed_column,
            symbol=self.submunition_dispensed_column,
            hover_data=[
                self.carrier_launch_angle_column,
                self.submunition_dispense_time_column,
                self.submunition_light_time_column,
                self.time_column,
            ],
            color_continuous_scale=COLOR_MAPS_RGB["parula"],
            title=f"Reachability at time t={time}",
            labels={
                self.px_column: "Position [m]",
                self.py_column: "Altitude [m]",
            },
        )
        fig.update_traces(marker={"size": 5})
        fig.update_layout(
            autosize=False,
            width=1200,
            height=800,
            font_family="Helvetica",
            legend_orientation="h",
        )
        fig.show()

    def plot_reachability_around_position_before_time_color_speed(
        self,
        x_start: float,
        x_end: float,
        y_start: float,
        y_end: float,
        time: float,
    ) -> None:
        """Plots the trajectory points within the given box before the given
        time.
        
        The color of the points denotes the speed.
        
        Args:
            x_start: x-position range start in meters.
            x_end: x-position range end in meters.
            y_start: y-position range start in meters.
            y_end: y_position range end in meters.
            time: Time in seconds.
        """
        # Find the trajectory points within the box before the given time.
        df_within_box = self.df[(self.df[self.px_column] >= x_start) &
                                (self.df[self.px_column] <= x_end) &
                                (self.df[self.py_column] >= y_start) &
                                (self.df[self.py_column] <= y_end) &
                                (self.df[self.time_column] < time)]

        # Plot the trajectory points in Matplotlib.
        fig, ax = plt.subplots(figsize=(12, 6))
        scatter = ax.scatter(
            df_within_box[self.px_column],
            df_within_box[self.py_column],
            s=3,
            c=df_within_box[self.speed_column],
            cmap=COLOR_MAPS["parula"],
        )
        ax.set_xlabel("Position [m]")
        ax.set_ylabel("Altitude [m]")
        ax.set_title(rf"Reachability within ${x_start} \leq x \leq {x_end}$ "
                     rf"and ${y_start} \leq y \leq {y_end}$")
        plt.colorbar(scatter)
        plt.show()

        # Plot the trajectory points separated by the submunition dispense time
        # in Matplotlib.
        fig, ax = plt.subplots(
            figsize=(12, 6),
            subplot_kw={"projection": "3d"},
        )
        scatter = ax.scatter(
            df_within_box[self.px_column],
            df_within_box[self.submunition_dispense_time_column],
            df_within_box[self.py_column],
            c=df_within_box[self.speed_column],
            cmap=COLOR_MAPS["parula"],
        )
        ax.set_xlabel("Position [m]")
        ax.set_ylabel("Submunition dispense time [s]")
        ax.set_zlabel("Altitude [m]")
        ax.set_title(rf"Reachability within ${x_start} \leq x \leq {x_end}$ "
                     rf"and ${y_start} \leq y \leq {y_end}$")
        plt.colorbar(scatter)
        plt.show()

        # Plot the trajectory points in Plotly.
        fig = px.scatter(
            df_within_box,
            x=self.px_column,
            y=self.py_column,
            color=self.speed_column,
            symbol=self.submunition_dispensed_column,
            hover_data=[
                self.carrier_launch_angle_column,
                self.submunition_dispense_time_column,
                self.submunition_light_time_column,
                self.time_column,
            ],
            color_continuous_scale=COLOR_MAPS_RGB["parula"],
            title=(f"Reachability within {x_start} <= x <= {x_end} and "
                   f"{y_start} <= y <= {y_end}"),
            labels={
                self.px_column: "Position [m]",
                self.py_column: "Altitude [m]",
            },
        )
        fig.update_traces(marker={"size": 5})
        fig.update_layout(
            autosize=False,
            width=1200,
            height=800,
            font_family="Helvetica",
            legend_orientation="h",
        )
        fig.show()

        # Plot the trajectory points separated by the submunition dispense time
        # in Plotly.
        fig = px.scatter_3d(
            df_within_box,
            x=self.px_column,
            y=self.submunition_dispense_time_column,
            z=self.py_column,
            color=self.speed_column,
            symbol=self.submunition_dispensed_column,
            hover_data=[
                self.carrier_launch_angle_column,
                self.submunition_dispense_time_column,
                self.submunition_light_time_column,
                self.time_column,
            ],
            color_continuous_scale=COLOR_MAPS_RGB["parula"],
            title=(f"Reachability within {x_start} <= x <= {x_end} and "
                   f"{y_start} <= y <= {y_end}"),
            labels={
                self.px_column:
                    "Position [m]",
                self.py_column:
                    "Altitude [m]",
                self.submunition_dispense_time_column:
                    "Submunition dispense time [s]",
            },
        )
        fig.update_traces(marker={"size": 3})
        fig.update_layout(
            autosize=False,
            width=1200,
            height=800,
            font_family="Helvetica",
            legend_orientation="h",
        )
        fig.show()

    def plot_reachability_around_position_before_time_color_time(
        self,
        x_start: float,
        x_end: float,
        y_start: float,
        y_end: float,
        time: float,
    ) -> None:
        """Plots the trajectory points within the given box before the given
        time.
        
        The color of the points denotes the time.
        
        Args:
            x_start: x-position range start in meters.
            x_end: x-position range end in meters.
            y_start: y-position range start in meters.
            y_end: y-position range end in meters.
            time: Time in seconds.
        """
        # Find the trajectory points within the box before the given time.
        df_within_box = self.df[(self.df[self.px_column] >= x_start) &
                                (self.df[self.px_column] <= x_end) &
                                (self.df[self.py_column] >= y_start) &
                                (self.df[self.py_column] <= y_end) &
                                (self.df[self.time_column] < time)]

        # Plot the trajectory points in Matplotlib.
        fig, ax = plt.subplots(figsize=(12, 6))
        scatter = ax.scatter(
            df_within_box[self.px_column],
            df_within_box[self.py_column],
            s=3,
            c=df_within_box[self.time_column],
            cmap=COLOR_MAPS["parula"].reversed(),
        )
        ax.set_xlabel("Position [m]")
        ax.set_ylabel("Altitude [m]")
        ax.set_title(rf"Reachability within ${x_start} \leq x \leq {x_end}$ "
                     rf"and ${y_start} \leq y \leq {y_end}$")
        plt.colorbar(scatter)
        plt.show()

        # Plot the trajectory points in Plotly.
        fig = px.scatter(
            df_within_box,
            x=self.px_column,
            y=self.py_column,
            color=self.time_column,
            symbol=self.submunition_dispensed_column,
            hover_data=[
                self.carrier_launch_angle_column,
                self.submunition_dispense_time_column,
                self.submunition_light_time_column,
                self.speed_column,
            ],
            color_continuous_scale=COLOR_MAPS_RGB["parula"][::-1],
            title=(f"Reachability within {x_start} <= x <= {x_end} and "
                   f"{y_start} <= y <= {y_end}"),
            labels={
                self.px_column: "Position [m]",
                self.py_column: "Altitude [m]",
            },
        )
        fig.update_traces(marker={"size": 5})
        fig.update_layout(
            autosize=False,
            width=1200,
            height=800,
            font_family="Helvetica",
            legend_orientation="h",
        )
        fig.show()

    def find_optimal_trajectories(
        self,
        x_start: float,
        x_end: float,
        x_step: float,
        x_interpolation_step: float,
        y_start: float,
        y_end: float,
        y_step: float,
        y_interpolation_step: float,
    ) -> None:
        """Finds the optimal trajectories that maximize speed or minimize time
        to intercept.

        For each 2D position, we find all trajectory points within a ball
        centered at that position. Afterwards, we find the trajectory point
        with the maximum speed or with the minimum time and plot these optimal
        trajectory points.
        
        Args:
            x_start: x-position range start in meters.
            x_end: x-position range end in meters.
            x_step: x-position range step in meters.
            x_interpolation_step: x-position interpolation step in meters.
            y_start: y-position range start in meters.
            y_end: y-position range end in meters.
            y_step: y-position range step in meters.
            y_interpolation_step: y-position interpolation step in meters.
        """
        # Find the optimal trajectory points for each position.
        max_speed_indices = []
        min_time_indices = []
        for x in np.arange(x_start, x_end + x_step, x_step):
            for y in np.arange(y_start, y_end + y_step, y_step):
                # Find all trajectory points within a ball centered at the
                # position.
                df_ball = (self.df[np.sqrt(
                    np.square((self.df[[self.px_column, self.py_column]] -
                               np.array([x, y])) /
                              np.array([x_step, y_step])).sum(axis=1)) <= 1])
                if len(df_ball) == 0:
                    continue

                # Find the index of the trajectory point with the maximum speed.
                max_speed_indices.append(df_ball[self.speed_column].idxmax())

                # Find the trajectory point with the minimum time.
                min_time_indices.append(df_ball[self.time_column].idxmin())

        # Plot the trajectory points with the maximum speed in Matplotlib.
        # The color of the points denotes the time.
        df_max_speed = self.df.iloc[np.unique(max_speed_indices)]
        fig, ax = plt.subplots(
            figsize=(12, 6),
            subplot_kw={"projection": "3d"},
        )
        scatter = ax.scatter(
            df_max_speed[self.px_column],
            df_max_speed[self.py_column],
            df_max_speed[self.speed_column],
            c=df_max_speed[self.time_column],
            cmap=COLOR_MAPS["parula"].reversed(),
        )
        ax.set_xlabel("Position [m]")
        ax.set_ylabel("Altitude [m]")
        ax.set_zlabel("Maximum speed [m/s]")
        ax.set_title("Trajectory points with maximum speed")
        plt.colorbar(scatter, label="Time [s]")
        plt.show()

        # Plot the trajectory points with the maximum speed in Plotly.
        # The color of the points denotes the time.
        fig = px.scatter_3d(
            df_max_speed,
            x=self.px_column,
            y=self.py_column,
            z=self.speed_column,
            color=self.time_column,
            symbol=self.submunition_dispensed_column,
            hover_data=[
                self.carrier_launch_angle_column,
                self.submunition_dispense_time_column,
                self.submunition_light_time_column,
            ],
            color_continuous_scale=COLOR_MAPS_RGB["parula"][::-1],
            title="Trajectory points with maximum speed",
            labels={
                self.px_column: "Position [m]",
                self.py_column: "Altitude [m]",
                self.speed_column: "Maximum speed [m/s]",
            },
        )
        fig.update_traces(marker={"size": 5})
        fig.update_layout(
            autosize=False,
            width=1200,
            height=800,
            font_family="Helvetica",
            legend_orientation="h",
        )
        fig.show()

        # Interpolate the trajectory points with the maximum speed.
        x = np.arange(
            df_max_speed[self.px_column].min(),
            df_max_speed[self.px_column].max() + x_interpolation_step,
            x_interpolation_step,
        )
        y = np.arange(
            df_max_speed[self.py_column].min(),
            df_max_speed[self.py_column].max() + y_interpolation_step,
            y_interpolation_step,
        )
        X, Y = np.meshgrid(x, y)

        # Interpolate the maximum speed.
        max_speed_interpolator = scipy.interpolate.CloughTocher2DInterpolator(
            df_max_speed[[self.px_column, self.py_column]],
            df_max_speed[self.speed_column],
        )
        max_speed_interpolated = max_speed_interpolator(X, Y)

        # Interpolate the carrier launch angle.
        max_speed_carrier_launch_angle_interpolator = (
            scipy.interpolate.CloughTocher2DInterpolator(
                df_max_speed[[self.px_column, self.py_column]],
                df_max_speed[self.carrier_launch_angle_column],
            ))
        max_speed_carrier_launch_angle_interpolated = (
            max_speed_carrier_launch_angle_interpolator(X, Y))

        # Plot the interpolated maximum speed in Matplotlib.
        fig, ax = plt.subplots(figsize=(12, 6))
        image = ax.imshow(
            max_speed_interpolated,
            cmap=COLOR_MAPS["parula"],
            origin="lower",
            extent=(
                df_max_speed[self.py_column].min() - 0.5,
                df_max_speed[self.py_column].max() - 0.5,
                df_max_speed[self.px_column].min() - 0.5,
                df_max_speed[self.px_column].max() - 0.5,
            ),
        )
        ax.contour(
            X,
            Y,
            max_speed_interpolated,
            colors="black",
        )
        ax.set_xlabel("Position [m]")
        ax.set_ylabel("Altitude [m]")
        ax.set_title("Maximum speed")
        plt.colorbar(image, label="Maximum speed [m/s]")
        plt.show()

        # Plot the interpolated maximum speed in Plotly 2D.
        fig = px.imshow(
            max_speed_interpolated,
            x=x,
            y=y,
            color_continuous_scale=COLOR_MAPS_RGB["parula"],
            origin="lower",
            title="Maximum speed",
            labels={
                "x": "Position [m]",
                "y": "Altitude [m]",
                "color": "Maximum speed [m/s]",
            },
        )
        fig.update_layout(
            autosize=False,
            width=1200,
            height=800,
            font_family="Helvetica",
        )
        fig.show()

        # Plot the interpolated maximum speed in Plotly 3D.
        fig = go.Figure(data=[
            go.Surface(
                x=x,
                y=y,
                z=max_speed_interpolated,
                colorscale=COLOR_MAPS_RGB["parula"],
                colorbar_title_text="Maximum speed [m/s]",
                contours={
                    "z": {
                        "show": True,
                    },
                },
            )
        ])
        fig.update_layout(
            title={"text": "Maximum speed"},
            scene={
                "xaxis": {
                    "title": "Position [m]",
                },
                "yaxis": {
                    "title": "Altitude [m]",
                },
                "zaxis": {
                    "title": "Maximum speed [m/s]",
                },
            },
            autosize=False,
            width=1200,
            height=800,
            font_family="Helvetica",
        )
        fig.show()

        # Plot the interpolated launch angle in Matplotlib.
        fig, ax = plt.subplots(figsize=(12, 6))
        image = ax.imshow(
            max_speed_carrier_launch_angle_interpolated,
            cmap=COLOR_MAPS["parula"],
            origin="lower",
            extent=(
                df_max_speed[self.py_column].min() - 0.5,
                df_max_speed[self.py_column].max() - 0.5,
                df_max_speed[self.px_column].min() - 0.5,
                df_max_speed[self.px_column].max() - 0.5,
            ),
        )
        ax.contour(
            X,
            Y,
            max_speed_carrier_launch_angle_interpolated,
            colors="black",
        )
        ax.set_xlabel("Position [m]")
        ax.set_ylabel("Altitude [m]")
        ax.set_title("Launch angle for maximum speed")
        plt.colorbar(image, label="Carrier launch angle [deg]")
        plt.show()

        # Plot the interpolated launch angle in Plotly 2D.
        fig = px.imshow(
            max_speed_carrier_launch_angle_interpolated,
            x=x,
            y=y,
            color_continuous_scale=COLOR_MAPS_RGB["parula"],
            origin="lower",
            title="Launch angle for maximum speed",
            labels={
                "x": "Position [m]",
                "y": "Altitude [m]",
                "color": "Carrier launch angle [deg]",
            },
        )
        fig.update_layout(
            autosize=False,
            width=1200,
            height=800,
            font_family="Helvetica",
        )
        fig.show()

        # Plot the interpolated launch angle in Plotly 3D.
        fig = go.Figure(data=[
            go.Surface(
                x=x,
                y=y,
                z=max_speed_carrier_launch_angle_interpolated,
                colorscale=COLOR_MAPS_RGB["parula"],
                colorbar_title_text="Carrier launch angle [deg]",
                contours={
                    "z": {
                        "show": True,
                    },
                },
            )
        ])
        fig.update_layout(
            title={"text": "Launch angle for maximum speed"},
            scene={
                "xaxis": {
                    "title": "Position [m]",
                },
                "yaxis": {
                    "title": "Altitude [m]",
                },
                "zaxis": {
                    "title": "Carrier launch angle [deg]",
                },
            },
            autosize=False,
            width=1200,
            height=800,
            font_family="Helvetica",
        )
        fig.show()

        # Plot the trajectory points with the minimum time in Matplotlib.
        # The color of the points denotes the speed.
        df_min_time = self.df.iloc[np.unique(min_time_indices)]
        fig, ax = plt.subplots(
            figsize=(12, 6),
            subplot_kw={"projection": "3d"},
        )
        scatter = ax.scatter(
            df_min_time[self.px_column],
            df_min_time[self.py_column],
            df_min_time[self.time_column],
            c=df_min_time[self.speed_column],
            cmap=COLOR_MAPS["parula"],
        )
        ax.set_xlabel("Position [m]")
        ax.set_ylabel("Altitude [m]")
        ax.set_zlabel("Minimum time [s]")
        ax.set_title("Trajectory points with minimum time")
        plt.colorbar(scatter, label="Speed [m/s]")
        plt.show()

        # Plot the trajectory points with the minimum time in Plotly.
        # The color of the points denotes the speed.
        fig = px.scatter_3d(
            df_min_time,
            x=self.px_column,
            y=self.py_column,
            z=self.time_column,
            color=self.speed_column,
            symbol=self.submunition_dispensed_column,
            hover_data=[
                self.carrier_launch_angle_column,
                self.submunition_dispense_time_column,
                self.submunition_light_time_column,
            ],
            color_continuous_scale=COLOR_MAPS_RGB["parula"],
            title="Trajectory points with minimum time",
            labels={
                self.px_column: "Position [m]",
                self.py_column: "Altitude [m]",
                self.time_column: "Minimum time [s]",
            },
        )
        fig.update_traces(marker={"size": 5})
        fig.update_layout(
            autosize=False,
            width=1200,
            height=800,
            font_family="Helvetica",
            legend_orientation="h",
        )
        fig.show()

        # Interpolate the trajectory points with the minimum time.
        x = np.arange(
            df_min_time[self.px_column].min(),
            df_min_time[self.px_column].max() + x_interpolation_step,
            x_interpolation_step,
        )
        y = np.arange(
            df_min_time[self.py_column].min(),
            df_min_time[self.py_column].max() + y_interpolation_step,
            y_interpolation_step,
        )
        X, Y = np.meshgrid(x, y)

        # Interpolate the minimum time.
        min_time_interpolator = scipy.interpolate.CloughTocher2DInterpolator(
            df_min_time[[self.px_column, self.py_column]],
            df_min_time[self.time_column],
        )
        min_time_interpolated = min_time_interpolator(X, Y)

        # Plot the interpolated minimum time in Matplotlib.
        fig, ax = plt.subplots(figsize=(12, 6))
        image = ax.imshow(
            min_time_interpolated,
            cmap=COLOR_MAPS["parula"].reversed(),
            origin="lower",
            extent=(
                df_min_time[self.py_column].min() - 0.5,
                df_min_time[self.py_column].max() - 0.5,
                df_min_time[self.px_column].min() - 0.5,
                df_min_time[self.px_column].max() - 0.5,
            ),
        )
        ax.contour(
            X,
            Y,
            min_time_interpolated,
            colors="black",
        )
        ax.set_xlabel("Position [m]")
        ax.set_ylabel("Altitude [m]")
        ax.set_title("Minimum time")
        plt.colorbar(image, label="Minimum time [s]")
        plt.show()

        # Plot the interpolated maximum speed in Plotly 2D.
        fig = px.imshow(
            min_time_interpolated,
            x=x,
            y=y,
            color_continuous_scale=COLOR_MAPS_RGB["parula"][::-1],
            origin="lower",
            title="Minimum time",
            labels={
                "x": "Position [m]",
                "y": "Altitude [m]",
                "color": "Minimum time [s]",
            },
        )
        fig.update_layout(
            autosize=False,
            width=1200,
            height=800,
            font_family="Helvetica",
        )
        fig.show()

        # Plot the interpolated minimum time in Plotly 3D.
        fig = go.Figure(data=[
            go.Surface(
                x=x,
                y=y,
                z=min_time_interpolated,
                colorscale=COLOR_MAPS_RGB["parula"][::-1],
                colorbar_title_text="Minimum time [s]",
                contours={
                    "z": {
                        "show": True,
                    },
                },
            )
        ])
        fig.update_layout(
            title={"text": "Minimum time"},
            scene={
                "xaxis": {
                    "title": "Position [m]",
                },
                "yaxis": {
                    "title": "Altitude [m]",
                },
                "zaxis": {
                    "title": "Minimum time [s]",
                },
            },
            autosize=False,
            width=1200,
            height=800,
            font_family="Helvetica",
        )
        fig.show()
