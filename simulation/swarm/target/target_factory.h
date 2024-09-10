// The target factory constructs targets based on its type.

#pragma once

#include <memory>
#include <stdexcept>
#include <utility>

#include "absl/strings/str_format.h"
#include "simulation/swarm/proto/agent.pb.h"
#include "simulation/swarm/target/drone.h"
#include "simulation/swarm/target/missile.h"
#include "simulation/swarm/target/target.h"

namespace swarm::target {

// Target factory.
class TargetFactory {
 public:
  TargetFactory() = default;

  // Create a target.
  template <typename... Args>
  std::unique_ptr<Target> CreateTarget(const TargetType type, Args&&... args) {
    switch (type) {
      case TargetType::DRONE: {
        return std::make_unique<Drone>(std::forward<Args>(args)...);
      }
      case TargetType::MISSILE: {
        return std::make_unique<Missile>(std::forward<Args>(args)...);
      }
      default: {
        throw std::invalid_argument(
            absl::StrFormat("Invalid target type: %d.", type));
      }
    }
  }
};

}  // namespace swarm::target
