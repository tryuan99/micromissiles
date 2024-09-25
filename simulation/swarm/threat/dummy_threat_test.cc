#include "simulation/swarm/threat/dummy_threat.h"

#include <gtest/gtest.h>

#include "simulation/swarm/proto/agent.pb.h"

namespace swarm::threat {
namespace {

// Maximum error tolerance.
constexpr double kMaxErrorTolerance = 1e-6;

class DummyThreatTest : public testing::Test {
 protected:
  DummyThreatTest() : threat_(DummyThreat(AgentConfig())) {}

  // Dummy threat.
  DummyThreat threat_;
};

TEST_F(DummyThreatTest, StaticConfig) {
  EXPECT_NEAR(threat_.static_config().hit_config().kill_probability(), 0,
              kMaxErrorTolerance);
}

}  // namespace
}  // namespace swarm::threat
