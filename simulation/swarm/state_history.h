// The state history maintains a list of the past states of an agent.

#pragma once

#include <cstdbool>
#include <list>

#include "simulation/swarm/proto/state.pb.h"

namespace swarm::state {

class StateHistory {
 public:
  // History record.
  struct Record {
    Record() = default;
    Record(const double t, const bool hit) : Record(t, hit, State()) {}
    Record(const double t, const bool hit, State state)
        : t(t), hit(hit), state(std::move(state)) {}

    // Time in s.
    double t = 0.0;

    // If true, the agent has hit or been hit.
    bool hit = false;

    // State of the agent.
    State state;
  };

  // Iterator types.
  using iterator = std::list<Record>::iterator;
  using const_iterator = std::list<Record>::const_iterator;
  using size_type = std::list<Record>::size_type;

  StateHistory() = default;

  StateHistory(const StateHistory&) = default;
  StateHistory& operator=(const StateHistory&) = default;

  // Return the number of the history records.
  size_type size() const { return records_.size(); }

  // Return the earliest history record.
  Record& front() { return records_.front(); }
  const Record& front() const { return records_.front(); }

  // Return the latest history record.
  Record& back() { return records_.back(); }
  const Record& back() const { return records_.back(); }

  // Add a new history record.
  void Add(Record record);

  // Update the latest history record.
  void UpdateLast(const Record& record);

  // Iterator overrides.
  iterator begin() { return records_.begin(); }
  const_iterator begin() const { return records_.cbegin(); }
  const_iterator cbegin() const { return begin(); }
  iterator end() { return records_.end(); }
  const_iterator end() const { return records_.cend(); }
  const_iterator cend() const { return end(); }

 private:
  // List of history records.
  std::list<Record> records_;
};

}  // namespace swarm::state
