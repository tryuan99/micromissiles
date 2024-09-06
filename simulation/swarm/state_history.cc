#include "simulation/swarm/state_history.h"

namespace swarm::state {

void StateHistory::Add(Record record) { records_.push_back(std::move(record)); }

void StateHistory::UpdateLast(const Record& record) {
  records_.back() = record;
}

}  // namespace swarm::state
