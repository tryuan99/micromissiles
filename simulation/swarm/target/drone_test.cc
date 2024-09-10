#include "simulation/swarm/target/drone.h"

#include <gtest/gtest.h>

#include "simulation/swarm/proto/agent.pb.h"

namespace swarm::target {
namespace {

// Maximum error tolerance.
constexpr double kMaxErrorTolerance = 1e-6;

class DroneTest : public testing::Test {
 protected:
  DroneTest() : target_(Drone(AgentConfig())) {}

  // Drone.
  Drone target_;
};

TEST_F(DroneTest, StaticConfig) {
  EXPECT_NEAR(target_.static_config().hit_config().kill_probability(), 0.9,
              kMaxErrorTolerance);
}

}  // namespace
}  // namespace swarm::target
