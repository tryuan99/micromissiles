#include "simulation/swarm/assignment/distance_assignment.h"

#include <Eigen/Dense>
#include <algorithm>
#include <deque>
#include <memory>
#include <unordered_set>
#include <vector>

#include "simulation/swarm/missile/missile.h"
#include "simulation/swarm/target/target.h"

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
    const std::vector<std::unique_ptr<missile::Missile>>& missiles,
    const std::vector<std::unique_ptr<target::Target>>& targets) {
  // Get the missile and target positions.
  std::vector<Eigen::Vector3d> missile_positions(missiles.size());
  std::transform(missiles.cbegin(), missiles.cend(), missile_positions.begin(),
                 [](const std::unique_ptr<missile::Missile>& missile) {
                   return missile->GetPosition();
                 });
  std::vector<Eigen::Vector3d> target_positions(targets.size());
  std::transform(targets.cbegin(), targets.cend(), target_positions.begin(),
                 [](const std::unique_ptr<target::Target>& target) {
                   return target->GetPosition();
                 });

  // Sort the missile-target distances.
  std::deque<MissileTargetDistance> missile_target_distances;
  for (int missile_index = 0; missile_index < missiles.size();
       ++missile_index) {
    if (missiles[missile_index]->assignable_to_target()) {
      for (int target_index = 0; target_index < targets.size();
           ++target_index) {
        if (!targets[target_index]->hit()) {
          const auto distance = (target_positions[target_index] -
                                 missile_positions[missile_index])
                                    .norm();
          missile_target_distances.emplace_back(missile_index, target_index,
                                                distance);
        }
      }
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
    assigned_missile_indices.reserve(missile_target_distances.size());
    std::unordered_set<int> assigned_target_indices;
    assigned_target_indices.reserve(missile_target_distances.size());
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
    static_cast<void>(std::remove_if(
        missile_target_distances.begin(), missile_target_distances.end(),
        [&](const MissileTargetDistance& missile_target_distance) {
          return assigned_missile_indices.contains(
              missile_target_distance.missile_index);
        }));
  }
}

}  // namespace swarm::assignment
