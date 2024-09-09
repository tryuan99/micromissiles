#include "simulation/swarm/missiles/missile_factory.h"

#include <gtest/gtest.h>

#include "simulation/swarm/proto/missile_config.pb.h"

namespace swarm::missile {
namespace {

// Maximum error tolerance.
constexpr double kMaxErrorTolerance = 1e-6;

class MissileFactoryTest : public testing::Test {
 protected:
  // Missile factory.
  MissileFactory missile_factory_;
};

TEST_F(MissileFactoryTest, CreateMissileMicromissile) {
  const auto missile = missile_factory_.CreateMissile(MissileType::MICROMISSILE,
                                                      MissileConfig());
  EXPECT_NEAR(missile->static_config().boost_config().boost_time(), 0.3,
              kMaxErrorTolerance);
  EXPECT_NEAR(missile->static_config().boost_config().boost_acceleration(), 350,
              kMaxErrorTolerance);
}

TEST_F(MissileFactoryTest, CreateMissileHydra70) {
  const auto missile =
      missile_factory_.CreateMissile(MissileType::HYDRA_70, MissileConfig());
  EXPECT_NEAR(missile->static_config().boost_config().boost_time(), 1,
              kMaxErrorTolerance);
  EXPECT_NEAR(missile->static_config().boost_config().boost_acceleration(), 100,
              kMaxErrorTolerance);
}

}  // namespace
}  // namespace swarm::missile
