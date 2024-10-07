#include "simulation/swarm/sensor/ideal_sensor.h"

#include <gtest/gtest.h>

#include <Eigen/Dense>
#include <numbers>

#include "simulation/swarm/agent.h"
#include "simulation/swarm/proto/state.pb.h"

namespace swarm::sensor {
namespace {

// Maximum error tolerance.
constexpr double kMaxErrorTolerance = 1e-6;

// Test parameter struct.
struct IdealSensorTestParam {
  // Agent position.
  Eigen::Vector3d agent_position;

  // Agent velocity.
  Eigen::Vector3d agent_velocity;

  // Target position.
  Eigen::Vector3d target_position;

  // Target velocity.
  Eigen::Vector3d target_velocity;

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

class IdealSensorTest : public testing::TestWithParam<IdealSensorTestParam> {
 protected:
  IdealSensorTest()
      : sensor_(IdealSensor(agent_)),
        agent_(agent::ModelAgent(GenerateAgentState(GetParam()))),
        target_(agent::ModelAgent(GenerateTargetState(GetParam()))) {}

  // Generate the agent state.
  static State GenerateAgentState(const IdealSensorTestParam& param) {
    const auto& agent_position = param.agent_position;
    const auto& agent_velocity = param.agent_velocity;
    State agent_state;
    agent_state.mutable_position()->set_x(agent_position(0));
    agent_state.mutable_position()->set_y(agent_position(1));
    agent_state.mutable_position()->set_z(agent_position(2));
    agent_state.mutable_velocity()->set_x(agent_velocity(0));
    agent_state.mutable_velocity()->set_y(agent_velocity(1));
    agent_state.mutable_velocity()->set_z(agent_velocity(2));
    return agent_state;
  }

  // Generate the target state.
  static State GenerateTargetState(const IdealSensorTestParam& param) {
    const auto& target_position = GetParam().target_position;
    const auto& target_velocity = GetParam().target_velocity;
    State target_state;
    target_state.mutable_position()->set_x(target_position(0));
    target_state.mutable_position()->set_y(target_position(1));
    target_state.mutable_position()->set_z(target_position(2));
    target_state.mutable_velocity()->set_x(target_velocity(0));
    target_state.mutable_velocity()->set_y(target_velocity(1));
    target_state.mutable_velocity()->set_z(target_velocity(2));
    return target_state;
  }

  // Ideal sensor.
  IdealSensor sensor_;

  // Agent.
  agent::ModelAgent agent_;

  // Target.
  agent::ModelAgent target_;
};

TEST_P(IdealSensorTest, SensePositionRange) {
  const auto expected_range = GetParam().expected_range;
  const auto sensor_output = sensor_.SensePosition(target_);
  EXPECT_NEAR(sensor_output.position().range(), expected_range,
              kMaxErrorTolerance);
}

TEST_P(IdealSensorTest, SensePositionAzimuth) {
  const auto expected_azimuth = GetParam().expected_azimuth;
  const auto sensor_output = sensor_.SensePosition(target_);
  EXPECT_NEAR(sensor_output.position().azimuth(), expected_azimuth,
              kMaxErrorTolerance);
}

TEST_P(IdealSensorTest, SensePositionElevation) {
  const auto expected_elevation = GetParam().expected_elevation;
  const auto sensor_output = sensor_.SensePosition(target_);
  EXPECT_NEAR(sensor_output.position().elevation(), expected_elevation,
              kMaxErrorTolerance);
}

TEST_P(IdealSensorTest, SenseVelocityRange) {
  const auto expected_range_rate = GetParam().expected_range_rate;
  const auto sensor_output = sensor_.SenseVelocity(target_);
  EXPECT_NEAR(sensor_output.velocity().range(), expected_range_rate,
              kMaxErrorTolerance);
}

TEST_P(IdealSensorTest, SenseVelocityAzimuth) {
  const auto expected_azimuth_velocity = GetParam().expected_azimuth_velocity;
  const auto sensor_output = sensor_.SenseVelocity(target_);
  EXPECT_NEAR(sensor_output.velocity().azimuth(), expected_azimuth_velocity,
              kMaxErrorTolerance);
}

TEST_P(IdealSensorTest, SenseVelocityElevation) {
  const auto expected_elevation_velocity =
      GetParam().expected_elevation_velocity;
  const auto sensor_output = sensor_.SenseVelocity(target_);
  EXPECT_NEAR(sensor_output.velocity().elevation(), expected_elevation_velocity,
              kMaxErrorTolerance);
}

INSTANTIATE_TEST_SUITE_P(AzimuthElevation, IdealSensorTest,
                         testing::Values(
                             // Boresight.
                             IdealSensorTestParam{
                                 .agent_position = Eigen::Vector3d{0, 0, 0},
                                 .agent_velocity = Eigen::Vector3d{0, 4, 0},
                                 .target_position = Eigen::Vector3d{0, 4, 0},
                                 .target_velocity = Eigen::Vector3d{2, 2, -1},
                                 .expected_range = 4,
                                 .expected_azimuth = 0,
                                 .expected_elevation = 0,
                                 .expected_range_rate = -2,
                                 .expected_azimuth_velocity = 2.0 / 4,
                                 .expected_elevation_velocity = -1.0 / 4,
                             },
                             // Starboard.
                             IdealSensorTestParam{
                                 .agent_position = Eigen::Vector3d{0, 0, 0},
                                 .agent_velocity = Eigen::Vector3d{0, 1, 0},
                                 .target_position = Eigen::Vector3d{5, 0, 0},
                                 .target_velocity = Eigen::Vector3d{2, 3, -1},
                                 .expected_range = 5,
                                 .expected_azimuth = std::numbers::pi / 2,
                                 .expected_elevation = 0,
                                 .expected_range_rate = 2,
                                 .expected_azimuth_velocity = -2.0 / 5,
                                 .expected_elevation_velocity = -1.0 / 5,
                             },
                             // Above.
                             IdealSensorTestParam{
                                 .agent_position = Eigen::Vector3d{0, 0, 0},
                                 .agent_velocity = Eigen::Vector3d{0, 1, 0},
                                 .target_position = Eigen::Vector3d{0, 0, 5},
                                 .target_velocity = Eigen::Vector3d{0, 2, 0},
                                 .expected_range = 5,
                                 .expected_azimuth = 0,
                                 .expected_elevation = std::numbers::pi / 2,
                                 .expected_range_rate = 0,
                                 .expected_azimuth_velocity = 0,
                                 .expected_elevation_velocity = -1.0 / 5,
                             }));

}  // namespace
}  // namespace swarm::sensor
