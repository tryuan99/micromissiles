#include "simulation/swarm/assignment/assignment.h"

#include <memory>
#include <vector>

#include "simulation/swarm/agent.h"

namespace swarm::assignment {

std::vector<int> Assignment::GetAssignableMissileIndices(
    const std::vector<std::unique_ptr<agent::Agent>>& missiles) {
  std::vector<int> assignable_missile_indices;
  assignable_missile_indices.reserve(missiles.size());
  for (int missile_index = 0; missile_index < missiles.size();
       ++missile_index) {
    if (missiles[missile_index]->assignable()) {
      assignable_missile_indices.emplace_back(missile_index);
    }
  }
  return assignable_missile_indices;
}

std::vector<int> Assignment::GetActiveTargetIndices(
    const std::vector<std::unique_ptr<agent::Agent>>& targets) {
  std::vector<int> active_target_indices;
  active_target_indices.reserve(targets.size());
  for (int target_index = 0; target_index < targets.size(); ++target_index) {
    if (!targets[target_index]->hit()) {
      active_target_indices.emplace_back(target_index);
    }
  }
  return active_target_indices;
}

}  // namespace swarm::assignment
