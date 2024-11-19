#include <cmath>
#include <cstdlib>
#include <numbers>

#include "base/base.h"
#include "base/commandlineflags.h"
#include "simulation/swarm/proto/simulator_config.pb.h"
#include "simulation/swarm/simulator.h"
#include "utils/protobuf.h"

DEFINE_string(simulator_config, "", "Simulator configuration file.");
DEFINE_string(output, "", "Output file.");
DEFINE_bool(animate, true, "If true, animate the trajectories.");
DEFINE_string(animation, "", "Animation file.");
DEFINE_float(t_end, 10, "Simulation end time in seconds.");

// Interceptor characterization.
DEFINE_float(launch_angle, 45, "Carrier launch angle in degrees.");
DEFINE_float(dispense_time, 5, "Submunition dispense time in seconds.");
DEFINE_float(light_time, 10, "Submunition light time in seconds.");

int main(int argc, char** argv) {
  base::Init(argc, argv);

  // Load the simulator configuration.
  auto simulator_config = utils::LoadProtobufTextFile<swarm::SimulatorConfig>(
      FLAGS(simulator_config));

  // Modify the simulator configuration according to the flags.
  const auto z = 1e-6;
  const auto x = z / std::tan(FLAGS(launch_angle) * std::numbers::pi / 180);
  auto* interceptor_config = simulator_config.mutable_interceptor_configs(0);
  interceptor_config->mutable_initial_state()->mutable_velocity()->set_x(x);
  interceptor_config->mutable_initial_state()->mutable_velocity()->set_z(z);
  interceptor_config->mutable_submunitions_config()
      ->mutable_launch_config()
      ->set_launch_time(FLAGS(dispense_time));
  interceptor_config->mutable_submunitions_config()
      ->mutable_agent_config()
      ->mutable_dynamic_config()
      ->mutable_launch_config()
      ->set_launch_time(FLAGS(light_time));

  // Simulate the agents.
  swarm::simulator::Simulator simulator(simulator_config);
  simulator.Run(FLAGS(t_end));
  // simulator.Plot(FLAGS(animate), FLAGS(animation));

  return EXIT_SUCCESS;
}
