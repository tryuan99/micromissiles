#include "simulation/swarm/assignment/round_robin_assignment.h"

#include <gtest/gtest.h>

#include <memory>
#include <unordered_map>
#include <vector>

#include "simulation/swarm/agent.h"
#include "simulation/swarm/interceptor/dummy_interceptor.h"
#include "simulation/swarm/proto/agent.pb.h"
#include "simulation/swarm/threat/dummy_threat.h"

namespace swarm::assignment {
namespace {

class RoundRobinAssignmentTest : public testing::Test {
 protected:
  RoundRobinAssignmentTest()
      : interceptors_(GenerateInterceptors()), threats_(GenerateThreats()) {}

  // Generate the interceptors.
  static std::vector<std::unique_ptr<agent::Agent>> GenerateInterceptors() {
    std::vector<std::unique_ptr<agent::Agent>> interceptors;
    AgentConfig interceptor_config;
    interceptor_config.mutable_initial_state()->mutable_position()->set_x(1);
    interceptor_config.mutable_initial_state()->mutable_position()->set_x(2);
    interceptor_config.mutable_initial_state()->mutable_position()->set_x(1);
    interceptors.emplace_back(
        std::make_unique<interceptor::DummyInterceptor>(interceptor_config));

    interceptor_config.mutable_initial_state()->mutable_position()->set_x(10);
    interceptor_config.mutable_initial_state()->mutable_position()->set_x(12);
    interceptor_config.mutable_initial_state()->mutable_position()->set_x(1);
    interceptors.emplace_back(
        std::make_unique<interceptor::DummyInterceptor>(interceptor_config));

    interceptor_config.mutable_initial_state()->mutable_position()->set_x(10);
    interceptor_config.mutable_initial_state()->mutable_position()->set_x(12);
    interceptor_config.mutable_initial_state()->mutable_position()->set_x(1);
    interceptors.emplace_back(
        std::make_unique<interceptor::DummyInterceptor>(interceptor_config));

    interceptor_config.mutable_initial_state()->mutable_position()->set_x(10);
    interceptor_config.mutable_initial_state()->mutable_position()->set_x(10);
    interceptor_config.mutable_initial_state()->mutable_position()->set_x(1);
    interceptors.emplace_back(
        std::make_unique<interceptor::DummyInterceptor>(interceptor_config));
    return interceptors;
  }

  // Generate the threats.
  static std::vector<std::unique_ptr<agent::Agent>> GenerateThreats() {
    std::vector<std::unique_ptr<agent::Agent>> threats;
    AgentConfig threat_config;
    threat_config.mutable_initial_state()->mutable_position()->set_x(10);
    threat_config.mutable_initial_state()->mutable_position()->set_x(15);
    threat_config.mutable_initial_state()->mutable_position()->set_x(2);
    threats.emplace_back(std::make_unique<threat::DummyThreat>(threat_config));

    threat_config.mutable_initial_state()->mutable_position()->set_x(1);
    threat_config.mutable_initial_state()->mutable_position()->set_x(2);
    threat_config.mutable_initial_state()->mutable_position()->set_x(2);
    threats.emplace_back(std::make_unique<threat::DummyThreat>(threat_config));
    return threats;
  }

  // Round-robin assignment.
  RoundRobinAssignment assignment_;

  // Interceptors.
  std::vector<std::unique_ptr<agent::Agent>> interceptors_;

  // Threats.
  std::vector<std::unique_ptr<agent::Agent>> threats_;
};

TEST_F(RoundRobinAssignmentTest, Assign) {
  assignment_.Assign(interceptors_, threats_);
  const auto& assignments = assignment_.assignments();
  std::unordered_map<int, int> expected_assignments{
      {0, 0}, {1, 1}, {2, 0}, {3, 1}};
  for (const auto& [interceptor_index, threat_index] : assignments) {
    EXPECT_EQ(expected_assignments[interceptor_index], threat_index);
  }
}

}  // namespace
}  // namespace swarm::assignment
