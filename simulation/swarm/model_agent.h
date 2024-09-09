// The model agent models an agent without any configuration.

#pragma once

#include "simulation/swarm/agent.h"
#include "simulation/swarm/proto/state.pb.h"

namespace swarm::agent {

// Model agent.
class ModelAgent : public Agent {
 public:
  ModelAgent() = default;
  explicit ModelAgent(const State initial_state)
      : Agent(std::move(initial_state)) {}

  ModelAgent(const ModelAgent&) = default;
  ModelAgent& operator=(const ModelAgent&) = default;
};

}  // namespace swarm::agent
