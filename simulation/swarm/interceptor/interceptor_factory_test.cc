#include "simulation/swarm/interceptor/interceptor_factory.h"

#include <gtest/gtest.h>

#include "simulation/swarm/proto/agent.pb.h"

namespace swarm::interceptor {
namespace {

// Maximum error tolerance.
constexpr double kMaxErrorTolerance = 1e-6;

class InterceptorFactoryTest : public testing::Test {
 protected:
  // Interceptor factory.
  InterceptorFactory interceptor_factory_;
};

TEST_F(InterceptorFactoryTest, CreateInterceptorMicromissile) {
  const auto interceptor = interceptor_factory_.CreateInterceptor(
      InterceptorType::MICROMISSILE, AgentConfig());
  EXPECT_NEAR(interceptor->static_config().boost_config().boost_time(), 0.3,
              kMaxErrorTolerance);
  EXPECT_NEAR(interceptor->static_config().boost_config().boost_acceleration(),
              350, kMaxErrorTolerance);
}

TEST_F(InterceptorFactoryTest, CreateInterceptorHydra70) {
  const auto interceptor = interceptor_factory_.CreateInterceptor(
      InterceptorType::HYDRA_70, AgentConfig());
  EXPECT_NEAR(interceptor->static_config().boost_config().boost_time(), 1,
              kMaxErrorTolerance);
  EXPECT_NEAR(interceptor->static_config().boost_config().boost_acceleration(),
              100, kMaxErrorTolerance);
}

}  // namespace
}  // namespace swarm::interceptor
