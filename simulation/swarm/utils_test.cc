#include "simulation/swarm/utils.h"

#include <gtest/gtest.h>

#include <string>

#include "simulation/swarm/proto/static_config.pb.h"

namespace swarm::utils {
namespace {

TEST(UtilsTest, LoadProtobufTextFileTest) {
  const std::string kStaticConfigFile =
      "simulation/swarm/configs/missile/micromissile.pbtxt";
  const auto static_config =
      LoadProtobufTextFile<StaticConfig>(kStaticConfigFile);
  EXPECT_TRUE(static_config.has_acceleration_config());
  EXPECT_TRUE(static_config.has_boost_config());
  EXPECT_TRUE(static_config.has_lift_drag_config());
  EXPECT_TRUE(static_config.has_body_config());
  EXPECT_TRUE(static_config.has_hit_config());
}

}  // namespace
}  // namespace swarm::utils
