#include "simulation/swarm/sensors/ideal_sensor.h"

#include <gtest/gtest.h>

#include <Eigen/Dense>

#include "simulation/swarm/model_agent.h"
#include "simulation/swarm/proto/agent.pb.h"
#include "simulation/swarm/proto/state.pb.h"

namespace swarm::sensor {
namespace {

// Maximum error tolerance.
constexpr double kMaxErrorTolerance = 1e-6;

class IdealSensorTest : public testing::Test {
 protected:
  // Agent state.
  const Eigen::Vector3d kAgentPosition{0, 0, 0};
  const Eigen::Vector3d kAgentVelocity{0, 4, 0};

  // Target state.
  const Eigen::Vector3d kTargetPosition{0, 4, 0};
  const Eigen::Vector3d kTargetVelocity{2, 2, -1};

  IdealSensorTest() : sensor_(IdealSensor(agent_)) {
    State agent_state;
    agent_state.mutable_position()->set_x(kAgentPosition(0));
    agent_state.mutable_position()->set_y(kAgentPosition(1));
    agent_state.mutable_position()->set_z(kAgentPosition(2));
    agent_state.mutable_velocity()->set_x(kAgentVelocity(0));
    agent_state.mutable_velocity()->set_y(kAgentVelocity(1));
    agent_state.mutable_velocity()->set_z(kAgentVelocity(2));
    agent_ = agent::ModelAgent(std::move(agent_state));

    State target_state;
    target_state.mutable_position()->set_x(kTargetPosition(0));
    target_state.mutable_position()->set_y(kTargetPosition(1));
    target_state.mutable_position()->set_z(kTargetPosition(2));
    target_state.mutable_velocity()->set_x(kTargetVelocity(0));
    target_state.mutable_velocity()->set_y(kTargetVelocity(1));
    target_state.mutable_velocity()->set_z(kTargetVelocity(2));
    target_ = agent::ModelAgent(std::move(target_state));
  }

  // Ideal sensor.
  IdealSensor sensor_;

  // Agent.
  agent::ModelAgent agent_;

  // Target.
  agent::ModelAgent target_;
};

TEST_F(IdealSensorTest, SensePositionRange) {
  const auto expected_range = kTargetPosition.norm();
  const auto sensor_output = sensor_.SensePosition(target_);
  EXPECT_NEAR(sensor_output.position().range(), expected_range,
              kMaxErrorTolerance);
}

TEST_F(IdealSensorTest, SensePositionAzimuth) {
  const auto expected_azimuth =
      std::atan(kTargetPosition(0) / kTargetPosition(1));
  const auto sensor_output = sensor_.SensePosition(target_);
  EXPECT_NEAR(sensor_output.position().azimuth(), expected_azimuth,
              kMaxErrorTolerance);
}

TEST_F(IdealSensorTest, SensePositionElevation) {
  const auto expected_elevation = std::atan(
      kTargetPosition(2) / std::sqrt(std::pow(kTargetPosition(0), 2) +
                                     std::pow(kTargetPosition(1), 2)));
  const auto sensor_output = sensor_.SensePosition(target_);
  EXPECT_NEAR(sensor_output.position().elevation(), expected_elevation,
              kMaxErrorTolerance);
}

TEST_F(IdealSensorTest, SenseVelocityRange) {
  const auto expected_range_rate = -2.0;
  const auto sensor_output = sensor_.SenseVelocity(target_);
  EXPECT_NEAR(sensor_output.velocity().range(), expected_range_rate,
              kMaxErrorTolerance);
}

TEST_F(IdealSensorTest, SenseVelocityAzimuth) {
  const auto expected_azimuth_velocity = 2.0 / 4;
  const auto sensor_output = sensor_.SenseVelocity(target_);
  EXPECT_NEAR(sensor_output.velocity().azimuth(), expected_azimuth_velocity,
              kMaxErrorTolerance);
}

TEST_F(IdealSensorTest, SenseVelocityElevation) {
  const auto expected_elevation_velocity = -1.0 / 4;
  const auto sensor_output = sensor_.SenseVelocity(target_);
  EXPECT_NEAR(sensor_output.velocity().elevation(), expected_elevation_velocity,
              kMaxErrorTolerance);
}

}  // namespace
}  // namespace swarm::sensor
