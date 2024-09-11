#include <cstdlib>

#include "base/base.h"
#include "base/commandlineflags.h"
#include "simulation/swarm/proto/swarm_config.pb.h"
#include "simulation/swarm/swarm_simulator.h"
#include "simulation/swarm/utils.h"

DEFINE_string(swarm_config, "", "Swarm configuration file.");
DEFINE_string(output, "", "Output file.");
DEFINE_bool(animate, true, "If true, animate the trajectories.");
DEFINE_string(animation, "", "Animation file.");
DEFINE_float(t_end, 10, "Simulation end time in seconds.");

int main(int argc, char** argv) {
  base::Init(argc, argv);

  // Load the swarm configuration.
  const auto swarm_config =
      swarm::utils::LoadProtobufTextFile<swarm::SwarmConfig>(
          FLAGS(swarm_config));

  // Simulate the swarms of agents.
  swarm::simulator::SwarmSimulator simulator(swarm_config);
  simulator.Run(FLAGS(t_end));
  simulator.Plot(FLAGS(animate), FLAGS(animation));

  return EXIT_SUCCESS;
}
