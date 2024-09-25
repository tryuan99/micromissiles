#include "simulation/swarm/interceptor/hydra_70.h"

#include <gtest/gtest.h>

#include "simulation/swarm/proto/agent.pb.h"

namespace swarm::interceptor {
namespace {

// Maximum error tolerance.
constexpr double kMaxErrorTolerance = 1e-6;

class Hydra70Test : public testing::Test {
 protected:
  Hydra70Test() : interceptor_(Hydra70(AgentConfig())) {}

  // Hydra-70.
  Hydra70 interceptor_;
};

TEST_F(Hydra70Test, StaticConfig) {
  EXPECT_NEAR(interceptor_.static_config().boost_config().boost_time(), 1,
              kMaxErrorTolerance);
  EXPECT_NEAR(interceptor_.static_config().boost_config().boost_acceleration(),
              100, kMaxErrorTolerance);
}

}  // namespace
}  // namespace swarm::interceptor
