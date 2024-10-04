#include "simulation/swarm/controls/solver/finite_horizon_discrete_time_lqr_solver.h"

#include <gtest/gtest.h>

#include <Eigen/Dense>

namespace swarm::controls::solver {
namespace {

class FiniteHorizonDiscreteTimeLqrSolverTest : public testing::Test {
 protected:
  FiniteHorizonDiscreteTimeLqrSolverTest()
      : solver_(FiniteHorizonDiscreteTimeLqrSolver(
            /*A=*/Eigen::Matrix2d{{0, 1}, {1, 0}}, /*B=*/Eigen::Vector2d{0, 1},
            /*Q=*/Eigen::Matrix2d{{1, 0}, {0, 1}},
            /*R=*/Eigen::Matrix<double, 1, 1>{{1}},
            /*Qf=*/Eigen::Matrix2d{{1, 0}, {0, 1}}, /*N=*/2)) {}

  // Finite-horizon, discrete-time LQR solver.
  FiniteHorizonDiscreteTimeLqrSolver solver_;
};

TEST_F(FiniteHorizonDiscreteTimeLqrSolverTest, GetFeedbackMatrix) {
  solver_.Solve();
  EXPECT_TRUE(solver_.GetFeedbackMatrix(/*time_step=*/0)
                  .isApprox(Eigen::Matrix<double, 1, 2>{2.0 / 3, 0}));
  EXPECT_TRUE(solver_.GetFeedbackMatrix(/*time_step=*/1)
                  .isApprox(Eigen::Matrix<double, 1, 2>{0.5, 0}));
}

TEST_F(FiniteHorizonDiscreteTimeLqrSolverTest, GetCostToGoMatrix) {
  solver_.Solve();
  EXPECT_TRUE(solver_.GetCostToGoMatrix(/*time_step=*/0)
                  .isApprox(Eigen::Matrix2d{{5.0 / 3, 0}, {0, 2.5}}));
  EXPECT_TRUE(solver_.GetCostToGoMatrix(/*time_step=*/1)
                  .isApprox(Eigen::Matrix2d{{1.5, 0}, {0, 2}}));
  EXPECT_TRUE(solver_.GetCostToGoMatrix(/*time_step=*/2)
                  .isApprox(Eigen::Matrix2d{{1, 0}, {0, 1}}));
  EXPECT_TRUE(solver_.GetCostToGoMatrix(/*time_step=*/0)
                  .isApprox(Eigen::Matrix2d{{5.0 / 3, 0}, {0, 2.5}}));
}

}  // namespace
}  // namespace swarm::controls::solver
