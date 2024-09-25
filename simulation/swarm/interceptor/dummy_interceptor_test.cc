#include "simulation/swarm/interceptor/dummy_interceptor.h"

#include <gtest/gtest.h>

#include "simulation/swarm/proto/agent.pb.h"

namespace swarm::interceptor {
namespace {

// Maximum error tolerance.
constexpr double kMaxErrorTolerance = 1e-6;

class DummyInterceptorTest : public testing::Test {
 protected:
  DummyInterceptorTest() : interceptor_(DummyInterceptor(AgentConfig())) {}

  // Dummy interceptor.
  DummyInterceptor interceptor_;
};

TEST_F(DummyInterceptorTest, StaticConfig) {
  EXPECT_NEAR(interceptor_.static_config().boost_config().boost_time(), 0,
              kMaxErrorTolerance);
  EXPECT_NEAR(interceptor_.static_config().boost_config().boost_acceleration(),
              0, kMaxErrorTolerance);
}

}  // namespace
}  // namespace swarm::interceptor
