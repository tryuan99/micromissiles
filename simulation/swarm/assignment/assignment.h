// The assignment class is an interface for assigning a threat to each
// interceptor.

#pragma once

#include <forward_list>
#include <memory>
#include <utility>
#include <vector>

#include "simulation/swarm/agent.h"

namespace swarm::assignment {

// Assignment interface.
class Assignment {
 public:
  // Assignment item type.
  // The first element corresponds to the interceptor index, and the second
  // element corresponds to the threat index.
  using AssignmentItem = std::pair<int, int>;

  Assignment() = default;

  Assignment(const Assignment&) = default;
  Assignment& operator=(const Assignment&) = default;

  virtual ~Assignment() = default;

  // Return the new interceptor-threat assignments.
  const std::forward_list<AssignmentItem>& assignments() const {
    return interceptor_to_threat_assignments_;
  }

  // Assign a threat to each interceptor that has not been assigned a threat
  // yet.
  void Assign(const std::vector<std::unique_ptr<agent::Agent>>& interceptors,
              const std::vector<std::unique_ptr<agent::Agent>>& threats) {
    interceptor_to_threat_assignments_.clear();
    AssignImpl(interceptors, threats);
  }

 protected:
  // Get the list of assignable interceptor indices.
  static std::vector<int> GetAssignableInterceptorIndices(
      const std::vector<std::unique_ptr<agent::Agent>>& interceptors);

  // Get the list of active threat indices.
  static std::vector<int> GetActiveThreatIndices(
      const std::vector<std::unique_ptr<agent::Agent>>& threats);

  // Assign a threat to each interceptor that has not been assigned a threat
  // yet.
  virtual void AssignImpl(
      const std::vector<std::unique_ptr<agent::Agent>>& interceptors,
      const std::vector<std::unique_ptr<agent::Agent>>& threats) = 0;

  // A list containing the interceptor-threat assignments.
  std::forward_list<AssignmentItem> interceptor_to_threat_assignments_;
};

}  // namespace swarm::assignment
