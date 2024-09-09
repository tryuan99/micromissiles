// The model agent models an agent without any configuration.

#pragma once

#include "simulation/swarm/agent.h"
#include "simulation/swarm/proto/state.pb.h"

namespace swarm::agent {

// Model agent.
template <typename T>
class ModelAgent : public Agent<T> {
 public:
  ModelAgent() = default;
  explicit ModelAgent(const State initial_state)
      : Agent<T>(std::move(initial_state)) {}

  ModelAgent(const ModelAgent&) = default;
  ModelAgent& operator=(const ModelAgent&) = default;
};

}  // namespace swarm::agent
