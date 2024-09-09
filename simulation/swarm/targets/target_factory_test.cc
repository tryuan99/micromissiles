#include "simulation/swarm/targets/target_factory.h"

#include <gtest/gtest.h>

#include "simulation/swarm/proto/target_config.pb.h"

namespace swarm::target {
namespace {

// Maximum error tolerance.
constexpr double kMaxErrorTolerance = 1e-6;

class TargetFactoryTest : public testing::Test {
 protected:
  // Target factory.
  TargetFactory target_factory_;
};

TEST_F(TargetFactoryTest, CreateTargetDrone) {
  const auto target =
      target_factory_.CreateTarget(TargetType::DRONE, TargetConfig());
  EXPECT_NEAR(target->static_config().hit_config().kill_probability(), 0.9,
              kMaxErrorTolerance);
}

TEST_F(TargetFactoryTest, CreateTargetMissile) {
  const auto target =
      target_factory_.CreateTarget(TargetType::MISSILE, TargetConfig());
  EXPECT_NEAR(target->static_config().hit_config().kill_probability(), 0.6,
              kMaxErrorTolerance);
}

}  // namespace
}  // namespace swarm::target
