#include "simulation/swarm/swarm_simulator.h"

#include "simulation/swarm/proto/simulator_config.pb.h"
#include "simulation/swarm/proto/state.pb.h"
#include "simulation/swarm/proto/swarm_config.pb.h"
#include "simulation/swarm/simulator.h"
#include "simulation/swarm/utils.h"

namespace swarm::simulator {

SimulatorConfig SwarmSimulator::GenerateSimulatorConfig(
    const SwarmConfig& swarm_config) {
  // Populate the simulator configuration.
  SimulatorConfig simulator_config;
  simulator_config.set_step_time(swarm_config.step_time());

  // Generate swarms of missiles.
  for (const auto& missile_swarm_config :
       swarm_config.missile_swarm_configs()) {
    for (int i = 0; i < missile_swarm_config.num_agents(); ++i) {
      auto* missile_config = simulator_config.add_missile_configs();
      missile_config->set_missile_type(
          missile_swarm_config.agent_config().missile_type());
      missile_config->mutable_initial_state()->CopyFrom(GenerateRandomState(
          missile_swarm_config.agent_config().initial_state(),
          missile_swarm_config.agent_config().standard_deviation()));
      missile_config->mutable_dynamic_config()->CopyFrom(
          missile_swarm_config.agent_config().dynamic_config());
      missile_config->mutable_plotting_config()->CopyFrom(
          missile_swarm_config.agent_config().plotting_config());
      missile_config->mutable_submunitions_config()->CopyFrom(
          missile_swarm_config.agent_config().submunitions_config());
    }
  }

  // Generate swarms of targets.
  for (const auto& target_swarm_config : swarm_config.target_swarm_configs()) {
    for (int i = 0; i < target_swarm_config.num_agents(); ++i) {
      auto* target_config = simulator_config.add_target_configs();
      target_config->set_target_type(
          target_swarm_config.agent_config().target_type());
      target_config->mutable_initial_state()->CopyFrom(GenerateRandomState(
          target_swarm_config.agent_config().initial_state(),
          target_swarm_config.agent_config().standard_deviation()));
      target_config->mutable_dynamic_config()->CopyFrom(
          target_swarm_config.agent_config().dynamic_config());
      target_config->mutable_plotting_config()->CopyFrom(
          target_swarm_config.agent_config().plotting_config());
      target_config->mutable_submunitions_config()->CopyFrom(
          target_swarm_config.agent_config().submunitions_config());
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
