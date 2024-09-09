#include "simulation/swarm/targets/dummy_target.h"

#include <gtest/gtest.h>

#include "simulation/swarm/proto/agent.pb.h"

namespace swarm::target {
namespace {

// Maximum error tolerance.
constexpr double kMaxErrorTolerance = 1e-6;

class DummyTargetTest : public testing::Test {
 protected:
  DummyTargetTest() : target_(DummyTarget(AgentConfig())) {}

  // Dummy target.
  DummyTarget target_;
};

TEST_F(DummyTargetTest, StaticConfig) {
  EXPECT_NEAR(target_.static_config().hit_config().kill_probability(), 0,
              kMaxErrorTolerance);
}

}  // namespace
}  // namespace swarm::target
