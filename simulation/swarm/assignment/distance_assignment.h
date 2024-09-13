// The distance assignment class assigns each missile to the nearest target that
// has not been assigned yet.

#pragma once

#include <memory>
#include <vector>

#include "simulation/swarm/agent.h"
#include "simulation/swarm/assignment/assignment.h"

namespace swarm::assignment {

class DistanceAssignment : public Assignment {
 public:
  DistanceAssignment() = default;

  DistanceAssignment(const DistanceAssignment&) = default;
  DistanceAssignment& operator=(const DistanceAssignment&) = default;

 protected:
  // Assign a target to each missile that has not been assigned a target yet.
  void AssignImpl(
      const std::vector<std::unique_ptr<agent::Agent>>& missiles,
      const std::vector<std::unique_ptr<agent::Agent>>& targets) override;
};

}  // namespace swarm::assignment
