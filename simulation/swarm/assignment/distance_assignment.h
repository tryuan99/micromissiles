// The distance assignment class assigns each missile to the nearest target that
// has not been assigned yet.

#pragma once

#include <memory>
#include <vector>

#include "simulation/swarm/assignment/assignment.h"
#include "simulation/swarm/missile/missile.h"
#include "simulation/swarm/target/target.h"

namespace swarm::assignment {

class DistanceAssignment : public Assignment {
 public:
  DistanceAssignment() = default;

  DistanceAssignment(const DistanceAssignment&) = default;
  DistanceAssignment& operator=(const DistanceAssignment&) = default;

  // Assign a target to each missile that has not been assigned a target yet.
  void Assign(
      const std::vector<std::unique_ptr<missile::Missile>>& missiles,
      const std::vector<std::unique_ptr<target::Target>>& targets) override;
};

}  // namespace swarm::assignment
