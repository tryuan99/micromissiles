#include "simulation/swarm/controls/mpc_controller.h"

#include <gtest/gtest.h>

#include <Eigen/Dense>

namespace swarm::controls {
namespace {

class MpcControllerTest : public testing::Test {
 protected:
  MpcControllerTest()
      : controller_(MpcController(
            /*A=*/Eigen::Matrix2d{{0, 1}, {0, 0}},
            /*B=*/Eigen::Vector2d{0, 1},
            /*sampling_time=*/2,
            /*Q=*/Eigen::MatrixXd{{0, 0}, {0, 0}},
            /*R=*/Eigen::Matrix<double, 1, 1>{{1}},
            /*Qf=*/Eigen::MatrixXd{{1, 0}, {0, 1}},
            /*horizon=*/2)) {}

  // MPC controller.
  MpcController controller_;
};

TEST_F(MpcControllerTest, GetOptimalControl) {
  const Eigen::Vector2d initial_state{1, -1};
  controller_.Plan(initial_state);
  EXPECT_TRUE(
      controller_
          .GetOptimalControl(
              /*input_bias_point=*/Eigen::Matrix<double, 1, 1>{{0}})
          .isApprox(Eigen::Matrix<double, 1, 1>{{-22.0 / 113 + 74.0 / 113}}));
  EXPECT_TRUE(controller_
                  .GetOptimalControl(
                      /*input_bias_point=*/Eigen::Matrix<double, 1, 1>{{5}})
                  .isApprox(Eigen::Matrix<double, 1, 1>{
                      {-22.0 / 113 + 74.0 / 113 + 5}}));
}

}  // namespace
}  // namespace swarm::controls
