// The target class is an interface for the dynamics of a single target.

#pragma once

#include <cstdbool>

#include "simulation/swarm/agent.h"
#include "simulation/swarm/proto/agent.pb.h"

namespace swarm::target {

// Target interface.
class Target : public agent::Agent {
 public:
  Target() = default;

  explicit Target(const AgentConfig& config) : Agent(config) {}
  Target(const AgentConfig& config, const double t_creation, const bool ready)
      : Agent(config, t_creation, ready) {}

  Target(const Target&) = default;
  Target& operator=(const Target&) = default;

  virtual ~Target() = default;

  // Return whether a target can be assigned to the target.
  bool assignable() const override { return false; };
};

}  // namespace swarm::target
