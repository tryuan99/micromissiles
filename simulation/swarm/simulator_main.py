import google.protobuf
from absl import app, flags

from simulation.swarm.proto.simulator_config_pb2 import SimulatorConfig
from simulation.swarm.simulator import Simulator

FLAGS = flags.FLAGS


def simulate_missiles_and_targets(simulator_config: str, output: str,
                                  t_end: float, t_step: float) -> None:
    """Simulates the missiles and the targets.

    Args:
        simulator_config: Simulator configuration.
        output: Output file.
        t_end: Simulation end time in seconds.
        t_step: Simulation step time in seconds.
    """
    # Parse the simulator configuration.
    with open(simulator_config, "r") as simulator_config_file:
        simulator_config = google.protobuf.text_format.Parse(
            simulator_config_file.read(), SimulatorConfig())

    simulator = Simulator(simulator_config)
    simulator.run(t_end, t_step)
    simulator.plot()


def main(argv):
    assert len(argv) == 1

    simulate_missiles_and_targets(
        FLAGS.simulator_config,
        FLAGS.output,
        FLAGS.t_end,
        FLAGS.t_step,
    )


if __name__ == "__main__":
    flags.DEFINE_string("simulator_config", None,
                        "Simulator configuration file.")
    flags.DEFINE_string("output", None, "output file.")
    flags.DEFINE_float("t_end", 10, "Simulation end time in seconds.")
    flags.DEFINE_float("t_step", 0.001, "Simulation step time in seconds.")
    flags.mark_flag_as_required("simulator_config")

    app.run(main)
