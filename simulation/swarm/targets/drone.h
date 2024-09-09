// The drone class represents the dynamics of a single drone.

#pragma once

#include <string>

#include "simulation/swarm/proto/target_config.pb.h"
#include "simulation/swarm/targets/target.h"
#include "simulation/swarm/utils.h"

namespace swarm::target {

// Drone.
class Drone : public Target {
 public:
  // Static configuration file.
  inline static const std::string kStaticConfigFile =
      "simulation/swarm/configs/targets/drone.pbtxt";

  Drone() = default;

  explicit Drone(const TargetConfig& config) : Target(config) {
    static_config_ = utils::LoadStaticConfigFromFile(kStaticConfigFile);
  }
  Drone(const TargetConfig& config, const double t_creation, const bool ready)
      : Target(config, t_creation, ready) {
    static_config_ = utils::LoadStaticConfigFromFile(kStaticConfigFile);
  }

  Drone(const Drone&) = default;
  Drone& operator=(const Drone&) = default;
};

}  // namespace swarm::target
