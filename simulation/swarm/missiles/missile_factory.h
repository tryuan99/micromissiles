// The missile factory constructs missiles based on its type.

#pragma once

#include <memory>
#include <stdexcept>
#include <utility>

#include "absl/strings/str_format.h"
#include "simulation/swarm/missiles/hydra_70.h"
#include "simulation/swarm/missiles/micromissile.h"
#include "simulation/swarm/missiles/missile.h"
#include "simulation/swarm/proto/agent.pb.h"

namespace swarm::missile {

// Missile factory.
class MissileFactory {
 public:
  MissileFactory() = default;

  // Create a missile.
  template <typename... Args>
  std::unique_ptr<Missile> CreateMissile(const MissileType type,
                                         Args&&... args) {
    switch (type) {
      case MissileType::MICROMISSILE: {
        return std::make_unique<Micromissile>(std::forward<Args>(args)...);
      }
      case MissileType::HYDRA_70: {
        return std::make_unique<Hydra70>(std::forward<Args>(args)...);
      }
      default: {
        throw std::invalid_argument(
            absl::StrFormat("Invalid missile type: %d.", type));
      }
    }
  }
};

}  // namespace swarm::missile
