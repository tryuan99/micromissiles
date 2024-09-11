#include "simulation/swarm/assignment/round_robin_assignment.h"

#include <algorithm>
#include <memory>
#include <vector>

#include "simulation/swarm/agent.h"

namespace swarm::assignment {

void RoundRobinAssignment::Assign(
    const std::vector<std::unique_ptr<agent::Agent>>& missiles,
    const std::vector<std::unique_ptr<agent::Agent>>& targets) {
  const auto assignable_missile_indices = GetAssignableMissileIndices(missiles);
  if (assignable_missile_indices.size() == 0) {
    return;
  }
  const auto active_target_indices = GetActiveTargetIndices(targets);
  if (active_target_indices.size() == 0) {
    return;
  }

  for (const auto missile_index : assignable_missile_indices) {
    const auto next_active_target_index_it =
        std::upper_bound(active_target_indices.cbegin(),
                         active_target_indices.cend(), prev_target_index_);
    const auto next_active_target_index =
        (next_active_target_index_it == active_target_indices.cend())
            ? 0
            : std::distance(active_target_indices.cbegin(),
                            next_active_target_index_it);
    const auto next_target_index =
        active_target_indices[next_active_target_index];
    missile_to_target_assignments_.emplace_front(missile_index,
                                                 next_target_index);
    prev_target_index_ = next_target_index;
  }
}

}  // namespace swarm::assignment
