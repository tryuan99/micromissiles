// The target class is an interface for the dynamics of a single target.

#pragma once

#include "simulation/swarm/agent.h"
#include "simulation/swarm/proto/target_config.pb.h"

namespace swarm::target {

// Target interface.
class Target : public agent::Agent<TargetConfig> {
 public:
  Target() = default;

  explicit Target(const TargetConfig& config) : Agent<TargetConfig>(config) {}
  Target(const TargetConfig& config, const double t_creation, const bool ready)
      : Agent<TargetConfig>(config, t_creation, ready) {}

  Target(const Target&) = default;
  Target& operator=(const Target&) = default;

  virtual ~Target() = default;
};

}  // namespace swarm::target
