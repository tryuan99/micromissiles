import google.protobuf
from absl import app, flags

from simulation.swarm.proto.simulator_config_pb2 import SimulatorConfig
from simulation.swarm.simulator import Simulator

FLAGS = flags.FLAGS


def simulate_missiles_and_targets(simulator_config: str, output: str,
                                  animation: str, t_end: float) -> None:
    """Simulates the missiles and the targets.

    Args:
        simulator_config: Simulator configuration.
        output: Output file.
        animation: Animation file.
        t_end: Simulation end time in seconds.
    """
    # Parse the simulator configuration.
    with open(simulator_config, "r") as simulator_config_file:
        simulator_config = google.protobuf.text_format.Parse(
            simulator_config_file.read(), SimulatorConfig())

    simulator = Simulator(simulator_config)
    simulator.run(t_end)
    simulator.plot(animation)


def main(argv):
    assert len(argv) == 1

    simulate_missiles_and_targets(
        FLAGS.simulator_config,
        FLAGS.output,
        FLAGS.animation,
        FLAGS.t_end,
    )


if __name__ == "__main__":
    flags.DEFINE_string("simulator_config", None,
                        "Simulator configuration file.")
    flags.DEFINE_string("output", None, "output file.")
    flags.DEFINE_string("animation", None, "Animation file.")
    flags.DEFINE_float("t_end", 10, "Simulation end time in seconds.")
    flags.mark_flag_as_required("simulator_config")

    app.run(main)
