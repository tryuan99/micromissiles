// The round-robin assignment class assigns interceptors to the threats in a
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
  // Assign a threat to each interceptor that has not been assigned a threat
  // yet.
  void AssignImpl(
      const std::vector<std::unique_ptr<agent::Agent>>& interceptors,
      const std::vector<std::unique_ptr<agent::Agent>>& threats) override;

 private:
  // Previous threat index that was assigned.
  int prev_threat_index_ = -1;
};

}  // namespace swarm::assignment
