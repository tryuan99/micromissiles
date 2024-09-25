// The threat class is an interface for the dynamics of a single threat.

#pragma once

#include <cstdbool>

#include "simulation/swarm/agent.h"
#include "simulation/swarm/proto/agent.pb.h"

namespace swarm::threat {

// Threat interface.
class Threat : public agent::Agent {
 public:
  Threat() = default;

  explicit Threat(const AgentConfig& config) : Agent(config) {}
  Threat(const AgentConfig& config, const double t_creation, const bool ready)
      : Agent(config, t_creation, ready) {}

  Threat(const Threat&) = default;
  Threat& operator=(const Threat&) = default;

  virtual ~Threat() = default;

  // Return whether a threat can be assigned to the threat.
  bool assignable() const override { return false; };
};

}  // namespace swarm::threat
