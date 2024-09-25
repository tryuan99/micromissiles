#include "simulation/swarm/interceptor/micromissile.h"

#include <gtest/gtest.h>

#include "simulation/swarm/proto/agent.pb.h"

namespace swarm::interceptor {
namespace {

// Maximum error tolerance.
constexpr double kMaxErrorTolerance = 1e-6;

class MicromissileTest : public testing::Test {
 protected:
  MicromissileTest() : interceptor_(Micromissile(AgentConfig())) {}

  // Micromissile.
  Micromissile interceptor_;
};

TEST_F(MicromissileTest, StaticConfig) {
  EXPECT_NEAR(interceptor_.static_config().boost_config().boost_time(), 0.3,
              kMaxErrorTolerance);
  EXPECT_NEAR(interceptor_.static_config().boost_config().boost_acceleration(),
              350, kMaxErrorTolerance);
}

}  // namespace
}  // namespace swarm::interceptor
