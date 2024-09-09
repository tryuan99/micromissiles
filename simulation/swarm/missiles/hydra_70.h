// The Hydra-70 class represents the dynamics of a single unguided Hydra-70
// rocket.

#pragma once

#include <cstdbool>
#include <memory>
#include <string>
#include <vector>

#include "simulation/swarm/agent.h"
#include "simulation/swarm/missiles/missile.h"
#include "simulation/swarm/proto/missile_config.pb.h"
#include "simulation/swarm/utils.h"

namespace swarm::missile {

// Hydra-70.
class Hydra70 : public Missile {
 public:
  // Static configuration file.
  inline static const std::string kStaticConfigFile =
      "simulation/swarm/configs/missiles/hydra_70.pbtxt";

  Hydra70() = default;

  explicit Hydra70(const MissileConfig& config) : Missile(config) {
    static_config_ = utils::LoadStaticConfigFromFile(kStaticConfigFile);
  }
  Hydra70(const MissileConfig& config, const double t_creation,
          const bool ready)
      : Missile(config, t_creation, ready) {
    static_config_ = utils::LoadStaticConfigFromFile(kStaticConfigFile);
  }

  Hydra70(const Hydra70&) = default;
  Hydra70& operator=(const Hydra70&) = default;

  // Return whether a target can be assigned to the missile.
  bool assignable_to_target() const override { return false; }

  // Spawn the submunitions.
  std::vector<std::unique_ptr<agent::Agent>> Spawn(double t);

 protected:
  // Update the agent's state in the midcourse flight phase.
  void UpdateMidCourse(double t) override;

 private:
  // Create a submunition based on its type.
  template <typename... Args>
  static std::unique_ptr<Missile> CreateSubmunition(const MissileType type,
                                                    Args&&... args);

  // If true, the Hydra-70 rocket has spawned its submunitions.
  bool has_spawned_ = false;
};

}  // namespace swarm::missile
