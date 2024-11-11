#include "simulation/swarm/controller/apn_controller.h"

#include <gtest/gtest.h>

#include <Eigen/Dense>

#include "simulation/swarm/agent.h"
#include "simulation/swarm/proto/state.pb.h"

namespace swarm::controller {
namespace {

class ApnControllerTest : public testing::Test {
 protected:
  ApnControllerTest()
      : agent_(agent::ModelAgent(GenerateAgentState())),
        target_(agent::ModelAgent(GenerateTargetState())),
        controller_(ApnController(agent_)) {
    agent_.AssignTarget(&target_);
  }

  // Generate the agent state.
  static State GenerateAgentState() {
    State agent_state;
    agent_state.mutable_velocity()->set_x(1);
    return agent_state;
  }

  // Generate the target state.
  static State GenerateTargetState() {
    State target_state;
    target_state.mutable_position()->set_x(10);
    target_state.mutable_velocity()->set_z(10);
    return target_state;
  }

  // Agent.
  agent::ModelAgent agent_;

  // Target.
  agent::ModelAgent target_;

  // Augmented proportional navigation controller.
  ApnController controller_;
};

TEST_F(ApnControllerTest, GetOptimalControlAzimuth) {
  controller_.Plan();
  EXPECT_TRUE(controller_.GetOptimalControl().isApprox(
      ApnController::kProportionalNavigationGain * Eigen::Vector3d{0, 0, 1}));
}

TEST_F(ApnControllerTest, GetOptimalControlElevation) {
  controller_.Plan();
  EXPECT_TRUE(controller_.GetOptimalControl().isApprox(
      ApnController::kProportionalNavigationGain * Eigen::Vector3d{0, 0, 1}));
}

}  // namespace
}  // namespace swarm::controller
