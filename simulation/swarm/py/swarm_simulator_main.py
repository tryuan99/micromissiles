import google.protobuf
from absl import app, flags
from simulation.swarm.proto.swarm_config_pb2 import SwarmConfig

from simulation.swarm.py.swarm_simulator import SwarmSimulator

FLAGS = flags.FLAGS


def simulate_missile_swarm_and_targets(swarm_config_file_path: str, output: str,
                                       animate: bool, animation: str,
                                       t_end: float) -> None:
    """Simulates the swarm of missiles and the targets.

    Args:
        swarm_config_file_path: Swarm configuration file path.
        output: Output file.
        animate: If true, animate the trajectories.
        animation: Animation file.
        t_end: Simulation end time in seconds.
    """
    # Parse the swarm configuration.
    with open(swarm_config_file_path, "r") as swarm_config_file:
        swarm_config = google.protobuf.text_format.Parse(
            swarm_config_file.read(), SwarmConfig())

    simulator = SwarmSimulator(swarm_config)
    simulator.run(t_end)
    simulator.plot(animate, animation)


def main(argv):
    assert len(argv) == 1

    simulate_missile_swarm_and_targets(
        FLAGS.swarm_config,
        FLAGS.output,
        FLAGS.animate,
        FLAGS.animation,
        FLAGS.t_end,
    )


if __name__ == "__main__":
    flags.DEFINE_string("swarm_config", None, "Swarm configuration file.")
    flags.DEFINE_string("output", None, "Output file.")
    flags.DEFINE_boolean("animate", True, "If true, animate the trajectories.")
    flags.DEFINE_string("animation", None, "Animation file.")
    flags.DEFINE_float("t_end", 10, "Simulation end time in seconds.")
    flags.mark_flag_as_required("swarm_config")

    app.run(main)
