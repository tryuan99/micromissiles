// The missile class represents the dynamics of a single missile.

#pragma once

#include <string>

#include "absl/strings/str_format.h"
#include "simulation/swarm/proto/target_config.pb.h"
#include "simulation/swarm/targets/target.h"
#include "simulation/swarm/utils.h"

namespace swarm::target {

// Missile.
class Missile : public Target {
 public:
  // Static configuration file.
  inline static const std::string kStaticConfigFile =
      "simulation/swarm/configs/targets/missile.pbtxt";

  Missile() = default;

  explicit Missile(const TargetConfig& config) : Target(config) {
    static_config_ = utils::LoadStaticConfigFromFile(kStaticConfigFile);
  }
  Missile(const TargetConfig& config, const double t_creation, const bool ready)
      : Target(config, t_creation, ready) {
    static_config_ = utils::LoadStaticConfigFromFile(kStaticConfigFile);
  }

  Missile(const Missile&) = default;
  Missile& operator=(const Missile&) = default;
};

}  // namespace swarm::target
