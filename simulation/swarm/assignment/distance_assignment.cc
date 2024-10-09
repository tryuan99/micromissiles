#include "simulation/swarm/assignment/distance_assignment.h"

#include <Eigen/Dense>
#include <algorithm>
#include <deque>
#include <memory>
#include <unordered_set>
#include <vector>

#include "simulation/swarm/agent.h"

namespace swarm::assignment {

namespace {
// Interceptor-threat distance tuple type.
struct InterceptorThreatDistance {
  InterceptorThreatDistance() = default;
  InterceptorThreatDistance(const int interceptor_index, const int threat_index,
                            const double distance)
      : interceptor_index(interceptor_index),
        threat_index(threat_index),
        distance(distance) {}

  // Interceptor index.
  int interceptor_index = 0;

  // Threat index.
  int threat_index = 0;

  // Distance.
  double distance = 0;
};
}  // namespace

void DistanceAssignment::AssignImpl(
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

  // Get the interceptor and threat positions.
  std::vector<Eigen::Vector3d> assignable_interceptor_positions(
      assignable_interceptor_indices.size());
  std::transform(
      assignable_interceptor_indices.cbegin(),
      assignable_interceptor_indices.cend(),
      assignable_interceptor_positions.begin(),
      [&](const int assignable_interceptor_index) {
        return interceptors[assignable_interceptor_index]->GetPosition();
      });
  std::vector<Eigen::Vector3d> active_threat_positions(
      active_threat_indices.size());
  std::transform(active_threat_indices.cbegin(), active_threat_indices.cend(),
                 active_threat_positions.begin(),
                 [&](const int active_threat_index) {
                   return threats[active_threat_index]->GetPosition();
                 });

  // Sort the interceptor-threat distances.
  std::deque<InterceptorThreatDistance> interceptor_threat_distances;
  for (int assignable_interceptor_index = 0;
       assignable_interceptor_index < assignable_interceptor_indices.size();
       ++assignable_interceptor_index) {
    for (int active_threat_index = 0;
         active_threat_index < active_threat_indices.size();
         ++active_threat_index) {
      const auto distance =
          (active_threat_positions[active_threat_index] -
           assignable_interceptor_positions[assignable_interceptor_index])
              .norm();
      interceptor_threat_distances.emplace_back(
          assignable_interceptor_indices[assignable_interceptor_index],
          active_threat_indices[active_threat_index], distance);
    }
  }
  std::sort(interceptor_threat_distances.begin(),
            interceptor_threat_distances.end(),
            [](const InterceptorThreatDistance& a,
               const InterceptorThreatDistance& b) {
              return (a.distance != b.distance)
                         ? (a.distance < b.distance)
                         : ((a.interceptor_index != b.interceptor_index)
                                ? (a.interceptor_index < b.interceptor_index)
                                : (a.threat_index < b.threat_index));
            });

  // Assign threats to interceptors based on distance.
  while (interceptor_threat_distances.size() > 0) {
    std::unordered_set<int> assigned_interceptor_indices;
    assigned_interceptor_indices.reserve(assignable_interceptor_indices.size());
    std::unordered_set<int> assigned_threat_indices;
    assigned_threat_indices.reserve(active_threat_indices.size());
    for (const auto& interceptor_threat_distance :
         interceptor_threat_distances) {
      const auto interceptor_index =
          interceptor_threat_distance.interceptor_index;
      const auto threat_index = interceptor_threat_distance.threat_index;
      if (!assigned_interceptor_indices.contains(interceptor_index) &&
          !assigned_threat_indices.contains(threat_index)) {
        interceptor_to_threat_assignments_.emplace_front(interceptor_index,
                                                         threat_index);
        assigned_interceptor_indices.emplace(interceptor_index);
        assigned_threat_indices.emplace(threat_index);
      }
    }
    interceptor_threat_distances.erase(
        std::remove_if(
            interceptor_threat_distances.begin(),
            interceptor_threat_distances.end(),
            [&](const InterceptorThreatDistance& interceptor_threat_distance) {
              return assigned_interceptor_indices.contains(
                  interceptor_threat_distance.interceptor_index);
            }),
        interceptor_threat_distances.cend());
  }
}

}  // namespace swarm::assignment
