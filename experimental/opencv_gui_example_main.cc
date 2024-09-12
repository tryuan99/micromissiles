#include <cstdlib>

#include "base/base.h"
#include "opencv2/core.hpp"
#include "opencv2/highgui.hpp"

int main(int argc, char** argv) {
  base::Init(argc, argv);

  cv::Mat matrix(16, 16, CV_64FC1);
  cv::randu(matrix, cv::Scalar(0), cv::Scalar(1));

  cv::namedWindow("Matrix", cv::WINDOW_NORMAL);
  cv::imshow("Matrix", matrix);
  cv::resizeWindow("Matrix", 800, 800);
  cv::waitKey(0);

  return EXIT_SUCCESS;
}
