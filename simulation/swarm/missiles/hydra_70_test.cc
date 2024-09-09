#include "simulation/swarm/missiles/hydra_70.h"

#include <gtest/gtest.h>

#include "simulation/swarm/proto/missile_config.pb.h"

namespace swarm::missile {
namespace {

// Maximum error tolerance.
constexpr double kMaxErrorTolerance = 1e-6;

class Hydra70Test : public testing::Test {
 protected:
  Hydra70Test() : missile_(Hydra70(MissileConfig())) {}

  // Hydra-70.
  Hydra70 missile_;
};

TEST_F(Hydra70Test, StaticConfig) {
  EXPECT_NEAR(missile_.static_config().boost_config().boost_time(), 1,
              kMaxErrorTolerance);
  EXPECT_NEAR(missile_.static_config().boost_config().boost_acceleration(), 100,
              kMaxErrorTolerance);
}

}  // namespace
}  // namespace swarm::missile
