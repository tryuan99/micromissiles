#include "simulation/swarm/missiles/micromissile.h"

#include <gtest/gtest.h>

#include "simulation/swarm/proto/missile_config.pb.h"

namespace swarm::missile {
namespace {

// Maximum error tolerance.
constexpr double kMaxErrorTolerance = 1e-6;

class MicromissileTest : public testing::Test {
 protected:
  MicromissileTest() : missile_(Micromissile(MissileConfig())) {}

  // Micromissile.
  Micromissile missile_;
};

TEST_F(MicromissileTest, StaticConfig) {
  EXPECT_NEAR(missile_.static_config().boost_config().boost_time(), 0.3,
              kMaxErrorTolerance);
  EXPECT_NEAR(missile_.static_config().boost_config().boost_acceleration(), 350,
              kMaxErrorTolerance);
}

}  // namespace
}  // namespace swarm::missile
