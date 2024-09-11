// The swarm simulator class generates a swarm of missiles placed at random
// positions and a swarm of targets placed at random positions with random
// velocities.

#pragma once

#include "simulation/swarm/proto/simulator_config.pb.h"
#include "simulation/swarm/proto/state.pb.h"
#include "simulation/swarm/proto/swarm_config.pb.h"
#include "simulation/swarm/simulator.h"

namespace swarm::simulator {

class SwarmSimulator : public Simulator {
 public:
  SwarmSimulator(const SwarmConfig& swarm_config)
      : Simulator(GenerateSimulatorConfig(swarm_config)) {}

  SwarmSimulator(const SwarmSimulator&) = delete;
  SwarmSimulator& operator=(const SwarmSimulator&) = delete;

 private:
  // Generate a simulator configuration.
  static SimulatorConfig GenerateSimulatorConfig(
      const SwarmConfig& swarm_config);

  // Generate a random state.
  static State GenerateRandomState(const State& mean,
                                   const State& standard_deviation);
};

}  // namespace swarm::simulator
