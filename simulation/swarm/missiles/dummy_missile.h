// The dummy missile class represents the dynamics of a single dummy missile.

#pragma once

#include "simulation/swarm/missiles/missile.h"
#include "simulation/swarm/proto/missile_config.pb.h"

namespace swarm::missile {

// Dummy missile.
class DummyMissile : public Missile {
 public:
  DummyMissile() = default;

  explicit DummyMissile(const MissileConfig& config) : Missile(config) {}
  DummyMissile(const MissileConfig& config, const double t_creation,
               const bool ready)
      : Missile(config, t_creation, ready) {}

  DummyMissile(const DummyMissile&) = default;
  DummyMissile& operator=(const DummyMissile&) = default;
};

}  // namespace swarm::missile
