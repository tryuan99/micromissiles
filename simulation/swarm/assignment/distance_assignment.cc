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
// Missile-target distance tuple type.
struct MissileTargetDistance {
  MissileTargetDistance() = default;
  MissileTargetDistance(const int missile_index, const int target_index,
                        const double distance)
      : missile_index(missile_index),
        target_index(target_index),
        distance(distance) {}

  // Missile index.
  int missile_index = 0;

  // Target index.
  int target_index = 0;

  // Distance.
  double distance = 0;
};
}  // namespace

void DistanceAssignment::Assign(
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

  // Get the missile and target positions.
  std::vector<Eigen::Vector3d> assignable_missile_positions(
      assignable_missile_indices.size());
  std::transform(assignable_missile_indices.cbegin(),
                 assignable_missile_indices.cend(),
                 assignable_missile_positions.begin(),
                 [&](const int assignable_missile_index) {
                   return missiles[assignable_missile_index]->GetPosition();
                 });
  std::vector<Eigen::Vector3d> active_target_positions(
      active_target_indices.size());
  std::transform(active_target_indices.cbegin(), active_target_indices.cend(),
                 active_target_positions.begin(),
                 [&](const int active_target_index) {
                   return targets[active_target_index]->GetPosition();
                 });

  // Sort the missile-target distances.
  std::deque<MissileTargetDistance> missile_target_distances;
  for (int assignable_missile_index = 0;
       assignable_missile_index < assignable_missile_indices.size();
       ++assignable_missile_index) {
    for (int active_target_index = 0;
         active_target_index < active_target_indices.size();
         ++active_target_index) {
      const auto distance =
          (active_target_positions[assignable_missile_index] -
           assignable_missile_positions[assignable_missile_index])
              .norm();
      missile_target_distances.emplace_back(
          assignable_missile_indices[assignable_missile_index],
          active_target_indices[active_target_index], distance);
    }
  }
  std::sort(missile_target_distances.begin(), missile_target_distances.end(),
            [](const MissileTargetDistance& a, const MissileTargetDistance& b) {
              return (a.distance != b.distance)
                         ? (a.distance < b.distance)
                         : ((a.missile_index != b.missile_index)
                                ? (a.missile_index < b.missile_index)
                                : (a.target_index < b.target_index));
            });

  // Assign targets to missiles based on distance.
  while (missile_target_distances.size() > 0) {
    std::unordered_set<int> assigned_missile_indices;
    assigned_missile_indices.reserve(assignable_missile_indices.size());
    std::unordered_set<int> assigned_target_indices;
    assigned_target_indices.reserve(active_target_indices.size());
    for (const auto& missile_target_distance : missile_target_distances) {
      const auto missile_index = missile_target_distance.missile_index;
      const auto target_index = missile_target_distance.target_index;
      if (!assigned_missile_indices.contains(missile_index) &&
          !assigned_target_indices.contains(target_index)) {
        missile_to_target_assignments_.emplace_front(missile_index,
                                                     target_index);
        assigned_missile_indices.emplace(missile_index);
        assigned_target_indices.emplace(target_index);
      }
    }
    missile_target_distances.erase(std::remove_if(
        missile_target_distances.begin(), missile_target_distances.end(),
        [&](const MissileTargetDistance& missile_target_distance) {
          return assigned_missile_indices.contains(
              missile_target_distance.missile_index);
        }));
  }
}

}  // namespace swarm::assignment
