#include "simulation/swarm/assignment/round_robin_assignment.h"

#include <gtest/gtest.h>

#include <memory>
#include <unordered_map>
#include <vector>

#include "simulation/swarm/agent.h"
#include "simulation/swarm/missile/dummy_missile.h"
#include "simulation/swarm/proto/agent.pb.h"
#include "simulation/swarm/target/dummy_target.h"

namespace swarm::assignment {
namespace {

class RoundRobinAssignmentTest : public testing::Test {
 protected:
  RoundRobinAssignmentTest()
      : missiles_(GenerateMissiles()), targets_(GenerateTargets()) {}

  // Generate the missiles.
  static std::vector<std::unique_ptr<agent::Agent>> GenerateMissiles() {
    std::vector<std::unique_ptr<agent::Agent>> missiles;
    AgentConfig missile_config;
    missile_config.mutable_initial_state()->mutable_position()->set_x(1);
    missile_config.mutable_initial_state()->mutable_position()->set_x(2);
    missile_config.mutable_initial_state()->mutable_position()->set_x(1);
    missiles.emplace_back(
        std::make_unique<missile::DummyMissile>(missile_config));

    missile_config.mutable_initial_state()->mutable_position()->set_x(10);
    missile_config.mutable_initial_state()->mutable_position()->set_x(12);
    missile_config.mutable_initial_state()->mutable_position()->set_x(1);
    missiles.emplace_back(
        std::make_unique<missile::DummyMissile>(missile_config));

    missile_config.mutable_initial_state()->mutable_position()->set_x(10);
    missile_config.mutable_initial_state()->mutable_position()->set_x(12);
    missile_config.mutable_initial_state()->mutable_position()->set_x(1);
    missiles.emplace_back(
        std::make_unique<missile::DummyMissile>(missile_config));

    missile_config.mutable_initial_state()->mutable_position()->set_x(10);
    missile_config.mutable_initial_state()->mutable_position()->set_x(10);
    missile_config.mutable_initial_state()->mutable_position()->set_x(1);
    missiles.emplace_back(
        std::make_unique<missile::DummyMissile>(missile_config));
    return missiles;
  }

  // Generate the targets.
  static std::vector<std::unique_ptr<agent::Agent>> GenerateTargets() {
    std::vector<std::unique_ptr<agent::Agent>> targets;
    AgentConfig target_config;
    target_config.mutable_initial_state()->mutable_position()->set_x(10);
    target_config.mutable_initial_state()->mutable_position()->set_x(15);
    target_config.mutable_initial_state()->mutable_position()->set_x(2);
    targets.emplace_back(std::make_unique<target::DummyTarget>(target_config));

    target_config.mutable_initial_state()->mutable_position()->set_x(1);
    target_config.mutable_initial_state()->mutable_position()->set_x(2);
    target_config.mutable_initial_state()->mutable_position()->set_x(2);
    targets.emplace_back(std::make_unique<target::DummyTarget>(target_config));
    return targets;
  }

  // Round-robin assignment.
  RoundRobinAssignment assignment_;

  // Missiles.
  std::vector<std::unique_ptr<agent::Agent>> missiles_;

  // Targets.
  std::vector<std::unique_ptr<agent::Agent>> targets_;
};

TEST_F(RoundRobinAssignmentTest, Assign) {
  assignment_.Assign(missiles_, targets_);
  const auto& assignments = assignment_.assignments();
  std::unordered_map<int, int> expected_assignments{
      {0, 0}, {1, 1}, {2, 0}, {3, 1}};
  for (const auto& [missile_index, target_index] : assignments) {
    EXPECT_EQ(expected_assignments[missile_index], target_index);
  }
}

}  // namespace
}  // namespace swarm::assignment
