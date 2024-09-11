#include "utils/thread_pool.h"

#include <gtest/gtest.h>

#include <mutex>

namespace utils {
namespace {

class ThreadPoolTest : public testing::Test {
 protected:
  // Number of threads.
  static constexpr int kNumThreads = 8;

  ThreadPoolTest() : thread_pool_(ThreadPool(kNumThreads)) {}

  void SetUp() override { thread_pool_.Start(); }

  void TearDown() override { thread_pool_.Stop(); }

  // Thread pool.
  ThreadPool thread_pool_;
};

TEST_F(ThreadPoolTest, Counter) {
  static constexpr int kNumCounts = 100;

  // Set up the counter.
  int counter = 0;
  std::mutex counter_mutex;
  const auto increment = [&]() {
    std::unique_lock<std::mutex> lock(counter_mutex);
    ++counter;
  };

  // Queue jobs to increment the counter.
  for (int i = 0; i < kNumCounts; ++i) {
    thread_pool_.QueueJob(increment);
  }

  // Wait for the thread pool.
  thread_pool_.Wait();
  EXPECT_EQ(counter, kNumCounts);
}

}  // namespace
}  // namespace utils
