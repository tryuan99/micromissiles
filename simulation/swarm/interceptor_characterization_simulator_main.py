import re
import subprocess

import numpy as np
from absl import app, flags, logging

FLAGS = flags.FLAGS

# Binary path.
SIMULATOR_MAIN = "simulation/swarm/simulator_main"
SIMULATOR_MAIN_PREFIX = "bazel-bin/simulation/swarm/simulator_main.runfiles/micromissiles/"
SIMULATOR_MAIN_ARGS = [
    "--simulator_config simulation/swarm/configs/simulator/single_interceptor.pbtxt",
    "--t_end 20",
    "--noanimate",
]


def simulate_trajectories(launch_angle_start: float, launch_angle_end: float,
                          dispense_time_start: float, dispense_time_end: float,
                          light_time_start: float, light_time_end: float,
                          output_csv: str) -> None:
    """Simulates the trajectories of the interceptor.

    Args:
        launch_angle_start: Launch angle range start in degrees.
        launch_angle_end: Launch angle range end in degrees.
        dispense_time_start: Dispense time range start in seconds.
        dispense_time_end: Dispense time range end in seconds.
        light_time_start: Light time range start in seconds.
        light_time_end: Light time range end in seconds.
        output_csv: Output csv.
    """
    with open(output_csv, "w") as csv_file:
        for launch_angle in np.arange(launch_angle_start, launch_angle_end + 5,
                                      5):
            for dispense_time in np.arange(dispense_time_start,
                                           dispense_time_end + 0.5, 0.5):
                for light_time in np.arange(light_time_start,
                                            light_time_end + 0.5, 0.5):
                    parameter_args = [
                        f"--launch_angle {launch_angle}",
                        f"--dispense_time {dispense_time}",
                        f"--light_time {light_time}",
                    ]
                    cmd = f"{SIMULATOR_MAIN_PREFIX + SIMULATOR_MAIN} {' '.join(SIMULATOR_MAIN_ARGS + parameter_args)}"
                    logging.info("Running command: %s", cmd)
                    subprocess.run(cmd,
                                   shell=True,
                                   stdout=subprocess.PIPE,
                                   stderr=csv_file)


def main(argv):
    assert len(argv) == 1

    simulate_trajectories(
        FLAGS.launch_angle_start,
        FLAGS.launch_angle_end,
        FLAGS.dispense_time_start,
        FLAGS.dispense_time_end,
        FLAGS.light_time_start,
        FLAGS.light_time_end,
        FLAGS.output_csv,
    )


if __name__ == "__main__":
    flags.DEFINE_float("launch_angle_start", 5,
                       "Launch angle range start in degrees.")
    flags.DEFINE_float("launch_angle_end", 85,
                       "Launch angle range start in degrees.")
    flags.DEFINE_float("dispense_time_start", 0,
                       "Dispense time range start in seconds.")
    flags.DEFINE_float("dispense_time_end", 10,
                       "Dispense time range end in seconds.")
    flags.DEFINE_float("light_time_start", 0,
                       "Light time range start in seconds.")
    flags.DEFINE_float("light_time_end", 10, "Light time range end in seconds.")
    flags.DEFINE_string("output_csv", None, "Output CSV file.")
    flags.mark_flag_as_required("output_csv")

    app.run(main)
