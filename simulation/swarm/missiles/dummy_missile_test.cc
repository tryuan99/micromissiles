#include "simulation/swarm/missiles/dummy_missile.h"

#include <gtest/gtest.h>

#include "simulation/swarm/proto/missile_config.pb.h"

namespace swarm::missile {
namespace {

// Maximum error tolerance.
constexpr double kMaxErrorTolerance = 1e-6;

class DummyMissileTest : public testing::Test {
 protected:
  DummyMissileTest() : missile_(DummyMissile(MissileConfig())) {}

  // Dummy missile.
  DummyMissile missile_;
};

TEST_F(DummyMissileTest, StaticConfig) {
  EXPECT_NEAR(missile_.static_config().boost_config().boost_time(), 0,
              kMaxErrorTolerance);
  EXPECT_NEAR(missile_.static_config().boost_config().boost_acceleration(), 0,
              kMaxErrorTolerance);
}

}  // namespace
}  // namespace swarm::missile
