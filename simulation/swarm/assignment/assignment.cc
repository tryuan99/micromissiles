#include "simulation/swarm/assignment/assignment.h"

#include <memory>
#include <vector>

#include "simulation/swarm/agent.h"

namespace swarm::assignment {

std::vector<int> Assignment::GetAssignableInterceptorIndices(
    const std::vector<std::unique_ptr<agent::Agent>>& interceptors) {
  std::vector<int> assignable_interceptor_indices;
  assignable_interceptor_indices.reserve(interceptors.size());
  for (int interceptor_index = 0; interceptor_index < interceptors.size();
       ++interceptor_index) {
    if (interceptors[interceptor_index]->assignable()) {
      assignable_interceptor_indices.emplace_back(interceptor_index);
    }
  }
  return assignable_interceptor_indices;
}

std::vector<int> Assignment::GetActiveThreatIndices(
    const std::vector<std::unique_ptr<agent::Agent>>& threats) {
  std::vector<int> active_threat_indices;
  active_threat_indices.reserve(threats.size());
  for (int threat_index = 0; threat_index < threats.size(); ++threat_index) {
    if (!threats[threat_index]->hit()) {
      active_threat_indices.emplace_back(threat_index);
    }
  }
  return active_threat_indices;
}

}  // namespace swarm::assignment
