#include "simulation/swarm/utils.h"

#include <gtest/gtest.h>

#include <string>

namespace swarm::utils {
namespace {

TEST(UtilsTest, LoadStaticConfigFromFileTest) {
  const std::string kStaticConfigFile =
      "simulation/swarm/configs/missiles/micromissile.pbtxt";
  const auto static_config = LoadStaticConfigFromFile(kStaticConfigFile);
  EXPECT_TRUE(static_config.has_acceleration_config());
  EXPECT_TRUE(static_config.has_boost_config());
  EXPECT_TRUE(static_config.has_lift_drag_config());
  EXPECT_TRUE(static_config.has_body_config());
  EXPECT_TRUE(static_config.has_hit_config());
}

}  // namespace
}  // namespace swarm::utils
