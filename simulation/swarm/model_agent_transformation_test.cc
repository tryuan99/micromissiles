#include <gtest/gtest.h>

#include <Eigen/Dense>
#include <numbers>

#include "simulation/swarm/agent.h"
#include "simulation/swarm/proto/state.pb.h"

namespace swarm::agent {
namespace {

// Maximum error tolerance.
constexpr double kMaxErrorTolerance = 1e-6;

// Test parameter struct.
struct ModelAgentTransformationTestParam {
  // Agent position.
  Eigen::Vector3d agent_position;

  // Agent velocity.
  Eigen::Vector3d agent_velocity;

  // Agent acceleration.
  Eigen::Vector3d agent_acceleration;

  // Target position.
  Eigen::Vector3d target_position;

  // Target velocity.
  Eigen::Vector3d target_velocity;

  // Target acceleration.
  Eigen::Vector3d target_acceleration;

  // Expected range.
  double expected_range = 0;

  // Expected azimuth.
  double expected_azimuth = 0;

  // Expected elevation.
  double expected_elevation = 0;

  // Expected range rate.
  double expected_range_rate = 0;

  // Expected azimuth velocity.
  double expected_azimuth_velocity = 0;

  // Expected elevation velocity.
  double expected_elevation_velocity = 0;
};

class ModelAgentTransformationTest
    : public testing::TestWithParam<ModelAgentTransformationTestParam> {
 protected:
  ModelAgentTransformationTest()
      : agent_(agent::ModelAgent(GenerateAgentState(GetParam()))),
        target_(agent::ModelAgent(GenerateTargetState(GetParam()))) {}

  // Generate the agent state.
  static State GenerateAgentState(
      const ModelAgentTransformationTestParam& param) {
    const auto& agent_position = param.agent_position;
    const auto& agent_velocity = param.agent_velocity;
    const auto& agent_acceleration = param.agent_acceleration;
    State agent_state;
    agent_state.mutable_position()->set_x(agent_position(0));
    agent_state.mutable_position()->set_y(agent_position(1));
    agent_state.mutable_position()->set_z(agent_position(2));
    agent_state.mutable_velocity()->set_x(agent_velocity(0));
    agent_state.mutable_velocity()->set_y(agent_velocity(1));
    agent_state.mutable_velocity()->set_z(agent_velocity(2));
    agent_state.mutable_acceleration()->set_x(agent_acceleration(0));
    agent_state.mutable_acceleration()->set_y(agent_acceleration(1));
    agent_state.mutable_acceleration()->set_z(agent_acceleration(2));
    return agent_state;
  }

  // Generate the target state.
  static State GenerateTargetState(
      const ModelAgentTransformationTestParam& param) {
    const auto& target_position = GetParam().target_position;
    const auto& target_velocity = GetParam().target_velocity;
    const auto& target_acceleration = GetParam().target_acceleration;
    State target_state;
    target_state.mutable_position()->set_x(target_position(0));
    target_state.mutable_position()->set_y(target_position(1));
    target_state.mutable_position()->set_z(target_position(2));
    target_state.mutable_velocity()->set_x(target_velocity(0));
    target_state.mutable_velocity()->set_y(target_velocity(1));
    target_state.mutable_velocity()->set_z(target_velocity(2));
    target_state.mutable_acceleration()->set_x(target_acceleration(0));
    target_state.mutable_acceleration()->set_y(target_acceleration(1));
    target_state.mutable_acceleration()->set_z(target_acceleration(2));
    return target_state;
  }

  // Agent.
  agent::ModelAgent agent_;

  // Target.
  agent::ModelAgent target_;
};

TEST_P(ModelAgentTransformationTest, RelativePositionRange) {
  const auto expected_range = GetParam().expected_range;
  const auto relative_transformation =
      agent_.GetRelativeTransformation(target_);
  EXPECT_NEAR(relative_transformation.position().range(), expected_range,
              kMaxErrorTolerance);
}

TEST_P(ModelAgentTransformationTest, RelativePositionAzimuth) {
  const auto expected_azimuth = GetParam().expected_azimuth;
  const auto relative_transformation =
      agent_.GetRelativeTransformation(target_);
  EXPECT_NEAR(relative_transformation.position().azimuth(), expected_azimuth,
              kMaxErrorTolerance);
}

TEST_P(ModelAgentTransformationTest, RelativePositionElevation) {
  const auto expected_elevation = GetParam().expected_elevation;
  const auto relative_transformation =
      agent_.GetRelativeTransformation(target_);
  EXPECT_NEAR(relative_transformation.position().elevation(),
              expected_elevation, kMaxErrorTolerance);
}

TEST_P(ModelAgentTransformationTest, RelativePositionCartesian) {
  const auto relative_transformation =
      agent_.GetRelativeTransformation(target_);
  Eigen::Vector3d position_cartesian{
      relative_transformation.position_cartesian().x(),
      relative_transformation.position_cartesian().y(),
      relative_transformation.position_cartesian().z()};
  EXPECT_TRUE(position_cartesian.isApprox(target_.GetPosition() -
                                          agent_.GetPosition()));
}

TEST_P(ModelAgentTransformationTest, RelativeVelocityRange) {
  const auto expected_range_rate = GetParam().expected_range_rate;
  const auto relative_transformation =
      agent_.GetRelativeTransformation(target_);
  EXPECT_NEAR(relative_transformation.velocity().range(), expected_range_rate,
              kMaxErrorTolerance);
}

TEST_P(ModelAgentTransformationTest, RelativeVelocityAzimuth) {
  const auto expected_azimuth_velocity = GetParam().expected_azimuth_velocity;
  const auto relative_transformation =
      agent_.GetRelativeTransformation(target_);
  EXPECT_NEAR(relative_transformation.velocity().azimuth(),
              expected_azimuth_velocity, kMaxErrorTolerance);
}

TEST_P(ModelAgentTransformationTest, RelativeVelocityElevation) {
  const auto expected_elevation_velocity =
      GetParam().expected_elevation_velocity;
  const auto relative_transformation =
      agent_.GetRelativeTransformation(target_);
  EXPECT_NEAR(relative_transformation.velocity().elevation(),
              expected_elevation_velocity, kMaxErrorTolerance);
}

TEST_P(ModelAgentTransformationTest, RelativeVelocityCartesian) {
  const auto relative_transformation =
      agent_.GetRelativeTransformation(target_);
  Eigen::Vector3d velocity_cartesian{
      relative_transformation.velocity_cartesian().x(),
      relative_transformation.velocity_cartesian().y(),
      relative_transformation.velocity_cartesian().z()};
  EXPECT_TRUE(velocity_cartesian.isApprox(target_.GetVelocity() -
                                          agent_.GetVelocity()));
}

TEST_P(ModelAgentTransformationTest, RelativeAccelerationCartesian) {
  const auto relative_transformation =
      agent_.GetRelativeTransformation(target_);
  Eigen::Vector3d acceleration_cartesian{
      relative_transformation.acceleration_cartesian().x(),
      relative_transformation.acceleration_cartesian().y(),
      relative_transformation.acceleration_cartesian().z()};
  EXPECT_TRUE(acceleration_cartesian.isApprox(target_.GetAcceleration()));
}

INSTANTIATE_TEST_SUITE_P(
    AzimuthElevation, ModelAgentTransformationTest,
    testing::Values(
        // Boresight.
        ModelAgentTransformationTestParam{
            .agent_position = Eigen::Vector3d{0, 0, 0},
            .agent_velocity = Eigen::Vector3d{0, 4, 0},
            .agent_acceleration = Eigen::Vector3d{1, 1, 1},
            .target_position = Eigen::Vector3d{0, 4, 0},
            .target_velocity = Eigen::Vector3d{2, 2, -1},
            .target_acceleration = Eigen::Vector3d{1, -1, 1},
            .expected_range = 4,
            .expected_azimuth = 0,
            .expected_elevation = 0,
            .expected_range_rate = -2,
            .expected_azimuth_velocity = 2.0 / 4,
            .expected_elevation_velocity = -1.0 / 4,
        },
        // Starboard.
        ModelAgentTransformationTestParam{
            .agent_position = Eigen::Vector3d{0, 0, 0},
            .agent_velocity = Eigen::Vector3d{0, 1, 0},
            .agent_acceleration = Eigen::Vector3d{1, 1, 1},
            .target_position = Eigen::Vector3d{5, 0, 0},
            .target_velocity = Eigen::Vector3d{2, 3, -1},
            .target_acceleration = Eigen::Vector3d{1, -1, 1},
            .expected_range = 5,
            .expected_azimuth = std::numbers::pi / 2,
            .expected_elevation = 0,
            .expected_range_rate = 2,
            .expected_azimuth_velocity = -2.0 / 5,
            .expected_elevation_velocity = -1.0 / 5,
        },
        // Above.
        ModelAgentTransformationTestParam{
            .agent_position = Eigen::Vector3d{0, 0, 0},
            .agent_velocity = Eigen::Vector3d{0, 1, 0},
            .agent_acceleration = Eigen::Vector3d{1, 1, 1},
            .target_position = Eigen::Vector3d{0, 0, 5},
            .target_velocity = Eigen::Vector3d{0, 2, 0},
            .target_acceleration = Eigen::Vector3d{1, -1, 1},
            .expected_range = 5,
            .expected_azimuth = 0,
            .expected_elevation = std::numbers::pi / 2,
            .expected_range_rate = 0,
            .expected_azimuth_velocity = 0,
            .expected_elevation_velocity = -1.0 / 5,
        }));

}  // namespace
}  // namespace swarm::agent
