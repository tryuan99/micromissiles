#include "simulation/swarm/state_history.h"

#include <gtest/gtest.h>

#include <cstdbool>

namespace swarm {
namespace {

class StateHistoryTest : public testing::Test {
 protected:
  // Number of history records.
  static constexpr int kNumRecords = 3;

  StateHistoryTest() {
    state_history_.Add(StateHistory::Record{
        .t = 0,
        .hit = false,
    });
    state_history_.Add(StateHistory::Record{
        .t = 1,
        .hit = false,
    });
    state_history_.Add(StateHistory::Record{
        .t = 2,
        .hit = false,
    });
  }

  // History of states.
  StateHistory state_history_;
};

TEST_F(StateHistoryTest, Add) {
  state_history_.Add(StateHistory::Record{
      .t = 10,
      .hit = true,
  });
  EXPECT_EQ(state_history_.size(), kNumRecords + 1);
  EXPECT_EQ(state_history_.back().t, 10);
  EXPECT_EQ(state_history_.back().hit, true);
}

TEST_F(StateHistoryTest, UpdateLast) {
  const auto new_record = StateHistory::Record{.t = 10, .hit = true};
  state_history_.UpdateLast(new_record);
  EXPECT_EQ(state_history_.size(), kNumRecords);
  EXPECT_EQ(state_history_.back().t, 10);
  EXPECT_EQ(state_history_.back().hit, true);
}

TEST_F(StateHistoryTest, ConstIterator) {
  double t = 0;
  for (const StateHistory::Record& record : state_history_) {
    EXPECT_EQ(record.t, t);
    EXPECT_EQ(record.hit, false);
    ++t;
  }
}

TEST_F(StateHistoryTest, Iterator) {
  for (auto& record : state_history_) {
    ++record.t;
  }
  double t = 1;
  for (const auto& record : state_history_) {
    EXPECT_EQ(record.t, t);
    EXPECT_EQ(record.hit, false);
    ++t;
  }
}

}  // namespace
}  // namespace swarm
