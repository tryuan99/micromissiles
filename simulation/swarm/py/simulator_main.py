import google.protobuf
from absl import app, flags
from simulation.swarm.proto.simulator_config_pb2 import SimulatorConfig

from simulation.swarm.py.simulator import Simulator

FLAGS = flags.FLAGS


def simulate_interceptors_and_threats(simulator_config_file_path: str,
                                      output: str, animate: bool,
                                      animation: str, t_end: float) -> None:
    """Simulates the interceptors and the threats.

    Args:
        simulator_config_file_path: Simulator configuration file path.
        output: Output file.
        animate: If true, animate the trajectories.
        animation: Animation file.
        t_end: Simulation end time in seconds.
    """
    # Parse the simulator configuration.
    with open(simulator_config_file_path, "r") as simulator_config_file:
        simulator_config = google.protobuf.text_format.Parse(
            simulator_config_file.read(), SimulatorConfig())

    simulator = Simulator(simulator_config)
    simulator.run(t_end)
    simulator.plot(animate, animation)


def main(argv):
    assert len(argv) == 1

    simulate_interceptors_and_threats(
        FLAGS.simulator_config,
        FLAGS.output,
        FLAGS.animate,
        FLAGS.animation,
        FLAGS.t_end,
    )


if __name__ == "__main__":
    flags.DEFINE_string("simulator_config", None,
                        "Simulator configuration file.")
    flags.DEFINE_string("output", None, "Output file.")
    flags.DEFINE_boolean("animate", True, "If true, animate the trajectories.")
    flags.DEFINE_string("animation", None, "Animation file.")
    flags.DEFINE_float("t_end", 10, "Simulation end time in seconds.")
    flags.mark_flag_as_required("simulator_config")

    app.run(main)
