#include "simulation/swarm/controls/discretizer.h"

#include <gtest/gtest.h>

#include <Eigen/Dense>

namespace swarm::controls::solver {
namespace {

class ForwardEulerDiscretizerTest : public testing::Test {
 protected:
  ForwardEulerDiscretizerTest()
      : discretizer_(ForwardEulerDiscretizer(
            /*A=*/Eigen::Matrix2d{{0, 1}, {0, 0}},
            /*B=*/Eigen::Vector2d{0, 1})) {}

  // Forward-Euler discretizer.
  ForwardEulerDiscretizer discretizer_;
};

TEST_F(ForwardEulerDiscretizerTest, DiscretizeA) {
  const auto discretized_system = discretizer_.Discretize(/*sampling_time=*/2);
  EXPECT_TRUE(
      discretized_system.first.isApprox(Eigen::Matrix2d{{1, 2}, {0, 1}}));
}

TEST_F(ForwardEulerDiscretizerTest, DiscretizeB) {
  const auto discretized_system = discretizer_.Discretize(/*sampling_time=*/2);
  EXPECT_TRUE(discretized_system.second.isApprox(Eigen::Vector2d{0, 2}));
}

class BackwardEulerDiscretizerTest : public testing::Test {
 protected:
  BackwardEulerDiscretizerTest()
      : discretizer_(BackwardEulerDiscretizer(
            /*A=*/Eigen::Matrix2d{{0, 1}, {0, 0}},
            /*B=*/Eigen::Vector2d{0, 1})) {}

  // Backward-Euler discretizer.
  BackwardEulerDiscretizer discretizer_;
};

TEST_F(BackwardEulerDiscretizerTest, DiscretizeA) {
  const auto discretized_system = discretizer_.Discretize(/*sampling_time=*/2);
  EXPECT_TRUE(
      discretized_system.first.isApprox(Eigen::Matrix2d{{1, 2}, {0, 1}}));
}

TEST_F(BackwardEulerDiscretizerTest, DiscretizeB) {
  const auto discretized_system = discretizer_.Discretize(/*sampling_time=*/2);
  EXPECT_TRUE(discretized_system.second.isApprox(Eigen::Vector2d{4, 2}));
}

class TrapezoidalDiscretizerTest : public testing::Test {
 protected:
  TrapezoidalDiscretizerTest()
      : discretizer_(TrapezoidalDiscretizer(
            /*A=*/Eigen::Matrix2d{{0, 1}, {0, 0}},
            /*B=*/Eigen::Vector2d{0, 1})) {}

  // Trapezoidal discretizer.
  TrapezoidalDiscretizer discretizer_;
};

TEST_F(TrapezoidalDiscretizerTest, DiscretizeA) {
  const auto discretized_system = discretizer_.Discretize(/*sampling_time=*/2);
  EXPECT_TRUE(
      discretized_system.first.isApprox(Eigen::Matrix2d{{1, 2}, {0, 1}}));
}

TEST_F(TrapezoidalDiscretizerTest, DiscretizeB) {
  const auto discretized_system = discretizer_.Discretize(/*sampling_time=*/2);
  EXPECT_TRUE(discretized_system.second.isApprox(Eigen::Vector2d{2, 2}));
}

}  // namespace
}  // namespace swarm::controls::solver
