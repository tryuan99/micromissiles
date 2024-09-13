#include "simulation/swarm/plotter/video_plotter.h"

#include <memory>
#include <vector>

#include "simulation/swarm/agent.h"

namespace swarm::plotter {

void VideoPlotter::PlotImpl(
    const double t_step,
    const std::vector<std::unique_ptr<agent::Agent>>& missiles,
    const std::vector<std::unique_ptr<agent::Agent>>& targets) {
  // TODO(titan): To be implemented.
}

}  // namespace swarm::plotter
