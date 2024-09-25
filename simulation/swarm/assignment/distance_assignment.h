// The distance assignment class assigns each interceptor to the nearest threat
// that has not been assigned yet.

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
  // Assign a threat to each interceptor that has not been assigned a threat
  // yet.
  void AssignImpl(
      const std::vector<std::unique_ptr<agent::Agent>>& interceptors,
      const std::vector<std::unique_ptr<agent::Agent>>& threats) override;
};

}  // namespace swarm::assignment
