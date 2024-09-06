// The model agent models an agent without any configuration.

#pragma once

#include "simulation/swarm/agent.h"
#include "simulation/swarm/proto/state.pb.h"
#include "simulation/swarm/proto/static_config.pb.h"

namespace swarm::agent {

// Model agent.
template <typename T>
class ModelAgent : public Agent<T> {
 public:
  ModelAgent() = default;
  ModelAgent(const State initial_state) : Agent<T>(std::move(initial_state)) {}

  ModelAgent(const ModelAgent&) = default;
  ModelAgent& operator=(const ModelAgent&) = default;

  // Return the static configuration of the dummy agent.
  const StaticConfig& static_config() const override { return static_config_; }

 private:
  // Static configuration.
  StaticConfig static_config_;
};

}  // namespace swarm::agent
