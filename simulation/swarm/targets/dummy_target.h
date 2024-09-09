// The dummy target class represents the dynamics of a single dummy target.

#pragma once

#include "simulation/swarm/proto/target_config.pb.h"
#include "simulation/swarm/targets/target.h"

namespace swarm::target {

// Dummy target.
class DummyTarget : public Target {
 public:
  DummyTarget() = default;

  explicit DummyTarget(const TargetConfig& config) : Target(config) {}
  DummyTarget(const TargetConfig& config, const double t_creation,
              const bool ready)
      : Target(config, t_creation, ready) {}

  DummyTarget(const DummyTarget&) = default;
  DummyTarget& operator=(const DummyTarget&) = default;
};

}  // namespace swarm::target
