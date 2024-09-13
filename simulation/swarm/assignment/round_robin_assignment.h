// The round-robin assignment class assigns missiles to the targets in a
// round-robin order.

#pragma once

#include <memory>
#include <vector>

#include "simulation/swarm/agent.h"
#include "simulation/swarm/assignment/assignment.h"

namespace swarm::assignment {

class RoundRobinAssignment : public Assignment {
 public:
  RoundRobinAssignment() = default;

  RoundRobinAssignment(const RoundRobinAssignment&) = default;
  RoundRobinAssignment& operator=(const RoundRobinAssignment&) = default;

 protected:
  // Assign a target to each missile that has not been assigned a target yet.
  void AssignImpl(
      const std::vector<std::unique_ptr<agent::Agent>>& missiles,
      const std::vector<std::unique_ptr<agent::Agent>>& targets) override;

 private:
  // Previous target index that was assigned.
  int prev_target_index_ = -1;
};

}  // namespace swarm::assignment
