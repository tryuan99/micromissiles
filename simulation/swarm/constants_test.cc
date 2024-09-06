#include "simulation/swarm/constants.h"

#include <gtest/gtest.h>

namespace swarm::constants {
namespace {

// Maximum error tolerance.
constexpr double kMaxErrorTolerance = 1e-6;

TEST(ConstantsTest, CalculateAirDensityAtAltitude) {
  EXPECT_EQ(CalculateAirDensityAtAltitude(/*altitude=*/0), kAirDensity);
  EXPECT_NEAR(CalculateAirDensityAtAltitude(/*altitude=*/100), 1.192479,
              kMaxErrorTolerance);
}

TEST(ConstantsTest, CalculateGravityAtAltitude) {
  EXPECT_EQ(CalculateGravityAtAltitude(/*altitude=*/0), kGravity);
  EXPECT_NEAR(CalculateGravityAtAltitude(/*altitude=*/100), 9.806342,
              kMaxErrorTolerance);
}

}  // namespace
}  // namespace swarm::constants
