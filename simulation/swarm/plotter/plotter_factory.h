// The plotter factory constructs a plotter based on plot type.

#pragma once

#include <memory>
#include <utility>

#include "simulation/swarm/plotter/plotter.h"
#include "simulation/swarm/plotter/static_plotter.h"
#include "simulation/swarm/plotter/video_plotter.h"

namespace swarm::plotter {

// Plotter factory.
class PlotterFactory {
 public:
  PlotterFactory() = default;

  // Create a plotter.
  template <typename... Args>
  std::unique_ptr<Plotter> CreatePlotter(const bool animate, Args&&... args) {
    if (animate) {
      return std::make_unique<VideoPlotter>(std::forward<Args>(args)...);
    }
    return std::make_unique<StaticPlotter>(std::forward<Args>(args)...);
  }
};

}  // namespace swarm::plotter
