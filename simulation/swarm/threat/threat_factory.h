// The threat factory constructs threats based on its type.

#pragma once

#include <memory>
#include <stdexcept>
#include <utility>

#include "absl/strings/str_format.h"
#include "simulation/swarm/proto/agent.pb.h"
#include "simulation/swarm/threat/drone.h"
#include "simulation/swarm/threat/missile.h"
#include "simulation/swarm/threat/threat.h"

namespace swarm::threat {

// Threat factory.
class ThreatFactory {
 public:
  ThreatFactory() = default;

  // Create a threat.
  template <typename... Args>
  std::unique_ptr<Threat> CreateThreat(const ThreatType type, Args&&... args) {
    switch (type) {
      case ThreatType::DRONE: {
        return std::make_unique<Drone>(std::forward<Args>(args)...);
      }
      case ThreatType::MISSILE: {
        return std::make_unique<Missile>(std::forward<Args>(args)...);
      }
      default: {
        throw std::invalid_argument(
            absl::StrFormat("Invalid threat type: %d.", type));
      }
    }
  }
};

}  // namespace swarm::threat
