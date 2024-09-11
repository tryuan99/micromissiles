#include <cstdlib>

#include "base/base.h"
#include "base/commandlineflags.h"
#include "simulation/swarm/proto/simulator_config.pb.h"
#include "simulation/swarm/simulator.h"
#include "simulation/swarm/utils.h"

DEFINE_string(simulator_config, "", "Simulator configuration file.");
DEFINE_string(output, "", "Output file.");
DEFINE_bool(animate, true, "If true, animate the trajectories.");
DEFINE_string(animation, "", "Animation file.");
DEFINE_float(t_end, 10, "Simulation end time in seconds.");

int main(int argc, char** argv) {
  base::Init(argc, argv);

  // Load the simulator configuration.
  const auto simulator_config =
      swarm::utils::LoadProtobufTextFile<swarm::SimulatorConfig>(
          FLAGS(simulator_config));

  // Simulate the agents.
  swarm::simulator::Simulator simulator(simulator_config);
  simulator.Run(FLAGS(t_end));
  simulator.Plot(FLAGS(animate), FLAGS(animation));

  return EXIT_SUCCESS;
}
