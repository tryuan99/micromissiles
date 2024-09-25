// The dummy threat class represents the dynamics of a single dummy threat.

#pragma once

#include "simulation/swarm/proto/agent.pb.h"
#include "simulation/swarm/threat/threat.h"

namespace swarm::threat {

// Dummy threat.
class DummyThreat : public Threat {
 public:
  DummyThreat() = default;

  explicit DummyThreat(const AgentConfig& config) : Threat(config) {}
  DummyThreat(const AgentConfig& config, const double t_creation,
              const bool ready)
      : Threat(config, t_creation, ready) {}

  DummyThreat(const DummyThreat&) = default;
  DummyThreat& operator=(const DummyThreat&) = default;
};

}  // namespace swarm::threat
