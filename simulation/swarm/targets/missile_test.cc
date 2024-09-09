#include "simulation/swarm/targets/missile.h"

#include <gtest/gtest.h>

#include "simulation/swarm/proto/target_config.pb.h"

namespace swarm::target {
namespace {

// Maximum error tolerance.
constexpr double kMaxErrorTolerance = 1e-6;

class MissileTest : public testing::Test {
 protected:
  MissileTest() : target_(Missile(TargetConfig())) {}

  // Missile.
  Missile target_;
};

TEST_F(MissileTest, StaticConfig) {
  EXPECT_NEAR(target_.static_config().hit_config().kill_probability(), 0.6,
              kMaxErrorTolerance);
}

}  // namespace
}  // namespace swarm::target
