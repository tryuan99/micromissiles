#include "simulation/swarm/assignment/round_robin_assignment.h"

#include <algorithm>
#include <memory>
#include <vector>

#include "simulation/swarm/agent.h"

namespace swarm::assignment {

void RoundRobinAssignment::AssignImpl(
    const std::vector<std::unique_ptr<agent::Agent>>& interceptors,
    const std::vector<std::unique_ptr<agent::Agent>>& threats) {
  const auto assignable_interceptor_indices =
      GetAssignableInterceptorIndices(interceptors);
  if (assignable_interceptor_indices.size() == 0) {
    return;
  }
  const auto active_threat_indices = GetActiveThreatIndices(threats);
  if (active_threat_indices.size() == 0) {
    return;
  }

  for (const auto interceptor_index : assignable_interceptor_indices) {
    const auto next_active_threat_index_it =
        std::upper_bound(active_threat_indices.cbegin(),
                         active_threat_indices.cend(), prev_threat_index_);
    const auto next_active_threat_index =
        (next_active_threat_index_it == active_threat_indices.cend())
            ? 0
            : std::distance(active_threat_indices.cbegin(),
                            next_active_threat_index_it);
    const auto next_threat_index =
        active_threat_indices[next_active_threat_index];
    interceptor_to_threat_assignments_.emplace_front(interceptor_index,
                                                     next_threat_index);
    prev_threat_index_ = next_threat_index;
  }
}

}  // namespace swarm::assignment
