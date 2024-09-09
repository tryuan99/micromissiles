#include "simulation/swarm/model_agent.h"

#include <gtest/gtest.h>

#include <Eigen/Dense>

#include "simulation/swarm/proto/state.pb.h"

namespace swarm::agent {
namespace {

// Maximum error tolerance.
constexpr double kMaxErrorTolerance = 1e-6;

class ModelAgentTest : public testing::Test {
 protected:
  // Agent velocity.
  const Eigen::Vector3d kAgentVelocity{-2, 1, 0};

  ModelAgentTest() {
    State agent_state;
    agent_state.mutable_velocity()->set_x(kAgentVelocity(0));
    agent_state.mutable_velocity()->set_y(kAgentVelocity(1));
    agent_state.mutable_velocity()->set_z(kAgentVelocity(2));
    agent_ = ModelAgent(std::move(agent_state));
  }

  // Model agent.
  ModelAgent agent_;
};

TEST_F(ModelAgentTest, GetPrincipalAxesRoll) {
  const auto principal_axes = agent_.GetPrincipalAxes();
  const Eigen::Vector3d expected_roll{-2, 1, 0};
  EXPECT_EQ(principal_axes.roll(0), expected_roll(0));
  EXPECT_EQ(principal_axes.roll(1), expected_roll(1));
  EXPECT_EQ(principal_axes.roll(2), expected_roll(2));
}

TEST_F(ModelAgentTest, GetPrincipalAxesPitch) {
  const auto principal_axes = agent_.GetPrincipalAxes();
  const Eigen::Vector3d expected_pitch{1, 2, 0};
  EXPECT_EQ(principal_axes.pitch(0), expected_pitch(0));
  EXPECT_EQ(principal_axes.pitch(1), expected_pitch(1));
  EXPECT_EQ(principal_axes.pitch(2), expected_pitch(2));
}

TEST_F(ModelAgentTest, GetPrincipalAxesYaw) {
  const auto principal_axes = agent_.GetPrincipalAxes();
  const Eigen::Vector3d expected_yaw{0, 0, 5};
  EXPECT_EQ(principal_axes.yaw(0), expected_yaw(0));
  EXPECT_EQ(principal_axes.yaw(1), expected_yaw(1));
  EXPECT_EQ(principal_axes.yaw(2), expected_yaw(2));
}

TEST_F(ModelAgentTest, GetNormalizedPrincipalAxesRoll) {
  const auto normalized_principal_axes = agent_.GetNormalizedPrincipalAxes();
  const Eigen::Vector3d expected_normalized_roll{-0.894427, 0.447214, 0};
  EXPECT_NEAR(normalized_principal_axes.roll(0), expected_normalized_roll(0),
              kMaxErrorTolerance);
  EXPECT_NEAR(normalized_principal_axes.roll(1), expected_normalized_roll(1),
              kMaxErrorTolerance);
  EXPECT_NEAR(normalized_principal_axes.roll(2), expected_normalized_roll(2),
              kMaxErrorTolerance);
}

TEST_F(ModelAgentTest, GetNormalizedPrincipalAxesPitch) {
  const auto normalized_principal_axes = agent_.GetNormalizedPrincipalAxes();
  const Eigen::Vector3d expected_normalized_pitch{0.447214, 0.894427, 0};
  EXPECT_NEAR(normalized_principal_axes.pitch(0), expected_normalized_pitch(0),
              kMaxErrorTolerance);
  EXPECT_NEAR(normalized_principal_axes.pitch(1), expected_normalized_pitch(1),
              kMaxErrorTolerance);
  EXPECT_NEAR(normalized_principal_axes.pitch(2), expected_normalized_pitch(2),
              kMaxErrorTolerance);
}

TEST_F(ModelAgentTest, GetNormalizedPrincipalAxesYaw) {
  const auto normalized_principal_axes = agent_.GetNormalizedPrincipalAxes();
  const Eigen::Vector3d expected_normalized_yaw{0, 0, 1};
  EXPECT_NEAR(normalized_principal_axes.yaw(0), expected_normalized_yaw(0),
              kMaxErrorTolerance);
  EXPECT_NEAR(normalized_principal_axes.yaw(1), expected_normalized_yaw(1),
              kMaxErrorTolerance);
  EXPECT_NEAR(normalized_principal_axes.yaw(2), expected_normalized_yaw(2),
              kMaxErrorTolerance);
}

}  // namespace
}  // namespace swarm::agent
