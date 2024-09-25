#include "simulation/swarm/threat/threat_factory.h"

#include <gtest/gtest.h>

#include "simulation/swarm/proto/agent.pb.h"

namespace swarm::threat {
namespace {

// Maximum error tolerance.
constexpr double kMaxErrorTolerance = 1e-6;

class ThreatFactoryTest : public testing::Test {
 protected:
  // Threat factory.
  ThreatFactory threat_factory_;
};

TEST_F(ThreatFactoryTest, CreateThreatDrone) {
  const auto threat =
      threat_factory_.CreateThreat(ThreatType::DRONE, AgentConfig());
  EXPECT_NEAR(threat->static_config().hit_config().kill_probability(), 0.9,
              kMaxErrorTolerance);
}

TEST_F(ThreatFactoryTest, CreateThreatMissile) {
  const auto threat =
      threat_factory_.CreateThreat(ThreatType::MISSILE, AgentConfig());
  EXPECT_NEAR(threat->static_config().hit_config().kill_probability(), 0.6,
              kMaxErrorTolerance);
}

}  // namespace
}  // namespace swarm::threat
