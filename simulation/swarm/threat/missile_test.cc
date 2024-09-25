#include "simulation/swarm/threat/missile.h"

#include <gtest/gtest.h>

#include "simulation/swarm/proto/agent.pb.h"

namespace swarm::threat {
namespace {

// Maximum error tolerance.
constexpr double kMaxErrorTolerance = 1e-6;

class MissileTest : public testing::Test {
 protected:
  MissileTest() : threat_(Missile(AgentConfig())) {}

  // Missile.
  Missile threat_;
};

TEST_F(MissileTest, StaticConfig) {
  EXPECT_NEAR(threat_.static_config().hit_config().kill_probability(), 0.6,
              kMaxErrorTolerance);
}

}  // namespace
}  // namespace swarm::threat
