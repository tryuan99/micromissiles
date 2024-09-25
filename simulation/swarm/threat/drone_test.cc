#include "simulation/swarm/threat/drone.h"

#include <gtest/gtest.h>

#include "simulation/swarm/proto/agent.pb.h"

namespace swarm::threat {
namespace {

// Maximum error tolerance.
constexpr double kMaxErrorTolerance = 1e-6;

class DroneTest : public testing::Test {
 protected:
  DroneTest() : threat_(Drone(AgentConfig())) {}

  // Drone.
  Drone threat_;
};

TEST_F(DroneTest, StaticConfig) {
  EXPECT_NEAR(threat_.static_config().hit_config().kill_probability(), 0.9,
              kMaxErrorTolerance);
}

}  // namespace
}  // namespace swarm::threat
