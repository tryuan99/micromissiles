#include "simulation/swarm/plotter/plotter.h"

#include <memory>
#include <vector>

#include "opencv2/viz.hpp"
#include "simulation/swarm/agent.h"

namespace swarm::plotter {

void Plotter::Plot(
    const double t_step,
    const std::vector<std::unique_ptr<agent::Agent>>& interceptors,
    const std::vector<std::unique_ptr<agent::Agent>>& threats) {
  cv::viz::WPlane ground_widget(cv::Size2d(5e4, 5e4), cv::viz::Color::gray());
  ground_widget.setRenderingProperty(cv::viz::OPACITY, 0.4);
  window_.showWidget("Ground", ground_widget);
  window_.showWidget("Coordinates", cv::viz::WCoordinateSystem());
  PlotImpl(t_step, interceptors, threats);
  window_.spin();
}

cv::viz::Color Plotter::GetColor(const Color color) {
  switch (color) {
    case Color::BLACK: {
      return cv::viz::Color::black();
    }
    case Color::BLUE: {
      return cv::viz::Color::blue();
    }
    case Color::ORANGE: {
      return cv::viz::Color::orange();
    }
    case Color::GREEN: {
      return cv::viz::Color::green();
    }
    case Color::RED: {
      return cv::viz::Color::red();
    }
    case Color::PURPLE: {
      return cv::viz::Color::purple();
    }
    case Color::BROWN: {
      return cv::viz::Color::brown();
    }
    case Color::PINK: {
      return cv::viz::Color::pink();
    }
    case Color::GRAY: {
      return cv::viz::Color::gray();
    }
    case Color::OLIVE: {
      return cv::viz::Color::olive();
    }
    case Color::CYAN: {
      return cv::viz::Color::cyan();
    }
    default: {
      return cv::viz::Color::white();
    }
  }
}

}  // namespace swarm::plotter
