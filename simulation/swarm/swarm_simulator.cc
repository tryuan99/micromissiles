#include "simulation/swarm/swarm_simulator.h"

#include "simulation/swarm/proto/simulator_config.pb.h"
#include "simulation/swarm/proto/state.pb.h"
#include "simulation/swarm/proto/swarm_config.pb.h"
#include "simulation/swarm/simulator.h"
#include "utils/random.h"

namespace swarm::simulator {

SimulatorConfig SwarmSimulator::GenerateSimulatorConfig(
    const SwarmConfig& swarm_config) {
  // Populate the simulator configuration.
  SimulatorConfig simulator_config;
  simulator_config.set_step_time(swarm_config.step_time());

  // Generate swarms of interceptors.
  for (const auto& interceptor_swarm_config :
       swarm_config.interceptor_swarm_configs()) {
    for (int i = 0; i < interceptor_swarm_config.num_agents(); ++i) {
      auto* interceptor_config = simulator_config.add_interceptor_configs();
      interceptor_config->set_interceptor_type(
          interceptor_swarm_config.agent_config().interceptor_type());
      interceptor_config->mutable_initial_state()->CopyFrom(GenerateRandomState(
          interceptor_swarm_config.agent_config().initial_state(),
          interceptor_swarm_config.agent_config().standard_deviation()));
      interceptor_config->mutable_dynamic_config()->CopyFrom(
          interceptor_swarm_config.agent_config().dynamic_config());
      interceptor_config->mutable_plotting_config()->CopyFrom(
          interceptor_swarm_config.agent_config().plotting_config());
      interceptor_config->mutable_submunitions_config()->CopyFrom(
          interceptor_swarm_config.agent_config().submunitions_config());
    }
  }

  // Generate swarms of threats.
  for (const auto& threat_swarm_config : swarm_config.threat_swarm_configs()) {
    for (int i = 0; i < threat_swarm_config.num_agents(); ++i) {
      auto* threat_config = simulator_config.add_threat_configs();
      threat_config->set_threat_type(
          threat_swarm_config.agent_config().threat_type());
      threat_config->mutable_initial_state()->CopyFrom(GenerateRandomState(
          threat_swarm_config.agent_config().initial_state(),
          threat_swarm_config.agent_config().standard_deviation()));
      threat_config->mutable_dynamic_config()->CopyFrom(
          threat_swarm_config.agent_config().dynamic_config());
      threat_config->mutable_plotting_config()->CopyFrom(
          threat_swarm_config.agent_config().plotting_config());
      threat_config->mutable_submunitions_config()->CopyFrom(
          threat_swarm_config.agent_config().submunitions_config());
    }
  }
  return simulator_config;
}

State SwarmSimulator::GenerateRandomState(const State& mean,
                                          const State& standard_deviation) {
  State state;
  // Randomly generate the position vector.
  state.mutable_position()->set_x(utils::GenerateRandomNormal(
      mean.position().x(), standard_deviation.position().x()));
  state.mutable_position()->set_y(utils::GenerateRandomNormal(
      mean.position().y(), standard_deviation.position().y()));
  state.mutable_position()->set_z(utils::GenerateRandomNormal(
      mean.position().z(), standard_deviation.position().z()));
  // Randomly generate the velocity vector.
  state.mutable_velocity()->set_x(utils::GenerateRandomNormal(
      mean.velocity().x(), standard_deviation.velocity().x()));
  state.mutable_velocity()->set_y(utils::GenerateRandomNormal(
      mean.velocity().y(), standard_deviation.velocity().y()));
  state.mutable_velocity()->set_z(utils::GenerateRandomNormal(
      mean.velocity().z(), standard_deviation.velocity().z()));
  return state;
}

}  // namespace swarm::simulator
