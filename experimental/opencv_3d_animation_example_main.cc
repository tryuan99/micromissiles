#include <cmath>
#include <cstdlib>
#include <numbers>
#include <vector>

#include "base/base.h"
#include "opencv2/core.hpp"
#include "opencv2/viz.hpp"

int main(int argc, char** argv) {
  base::Init(argc, argv);

  cv::viz::Viz3d window("Window");

  cv::viz::WPlane ground_widget(cv::Size2d(20, 20), cv::viz::Color::gray());
  window.showWidget("Ground", ground_widget);

  window.showWidget("Coordinates", cv::viz::WCoordinateSystem());

  cv::viz::WCube cube_widget(cv::Point3f(0.5, 0.5, 0), cv::Point3f(0, 0, -0.5),
                             /*wireframe=*/false, cv::viz::Color::blue());
  cube_widget.setRenderingProperty(cv::viz::LINE_WIDTH, 4);
  window.showWidget("Cube", cube_widget);

  cv::Point3d cone_center(0, 0, 0);
  cv::viz::WCone cone_widget(/*radius=*/0.2, cone_center,
                             cone_center + cv::Point3d{0, 0, 0.5},
                             /*resolution=*/6, cv::viz::Color::red());
  window.showWidget("Cone", cone_widget);

  std::vector<cv::Affine3d> cone_trajectory{
      {cv::Affine3d(cv::Mat::eye(3, 3, CV_64F), cv::Vec3d::zeros()),
       cv::Affine3d(cv::Mat::eye(3, 3, CV_64F), cv::Vec3d(1, 2, 2))}};
  cv::viz::WTrajectory cone_trajectory_widget(cone_trajectory);
  window.showWidget("Cone Trajectory", cone_trajectory_widget);

  double translation_phase = 0;
  double rotation_phase = 0;
  cv::Mat rotation_matrix = cv::Mat::zeros(3, 3, CV_64F);
  rotation_matrix.at<double>(0, 0) = 1;
  while (!window.wasStopped()) {
    translation_phase += std::numbers::pi * 0.01;

    rotation_phase += std::numbers::pi * 0.01;
    rotation_matrix.at<double>(1, 1) = std::cos(rotation_phase);
    rotation_matrix.at<double>(2, 1) = std::sin(rotation_phase);
    rotation_matrix.at<double>(1, 2) = -std::sin(rotation_phase);
    rotation_matrix.at<double>(2, 2) = std::cos(rotation_phase);

    cv::Affine3d pose(
        rotation_matrix,
        cv::Vec3d(std::cos(translation_phase), std::sin(translation_phase), 0));
    cube_widget.setPose(pose);

    window.spinOnce(/*time=*/1, /*force_redraw=*/false);
  }

  return EXIT_SUCCESS;
}
