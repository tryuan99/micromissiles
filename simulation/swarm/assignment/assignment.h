// The assignment class is an interface for assigning a target to each missile.

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
  // The first element corresponds to the missile index, and the second element
  // corresponds to the target index.
  using AssignmentItem = std::pair<int, int>;

  Assignment() = default;

  Assignment(const Assignment&) = default;
  Assignment& operator=(const Assignment&) = default;

  virtual ~Assignment() = default;

  // Return the missile-target assignments.
  const std::forward_list<AssignmentItem>& assignments() const {
    return missile_to_target_assignments_;
  }

  // Assign a target to each missile that has not been assigned a target yet.
  virtual void Assign(
      const std::vector<std::unique_ptr<agent::Agent>>& missiles,
      const std::vector<std::unique_ptr<agent::Agent>>& targets) = 0;

 protected:
  // Get the list of assignable missile indices.
  static std::vector<int> GetAssignableMissileIndices(
      const std::vector<std::unique_ptr<agent::Agent>>& missiles);

  // Get the list of active target indices.
  static std::vector<int> GetActiveTargetIndices(
      const std::vector<std::unique_ptr<agent::Agent>>& targets);

  // A list containing the missile-target assignments.
  std::forward_list<AssignmentItem> missile_to_target_assignments_;
};

}  // namespace swarm::assignment
