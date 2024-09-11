// The thread pool is a collection of threads to which jobs can be submitted.

#pragma once

#include <condition_variable>
#include <cstdbool>
#include <functional>
#include <mutex>
#include <queue>
#include <thread>
#include <vector>

namespace utils {

class ThreadPool {
 public:
  // Job type.
  using ThreadPoolJob = std::function<void()>;

  ThreadPool(const int num_threads) : num_threads_(num_threads) {
    threads_.reserve(num_threads_);
  }

  // Start the threads.
  void Start();

  // Stop the threads.
  void Stop();

  // Returns whether the thread pool is busy.
  bool busy() const {
    return num_threads_ != num_waiting_threads_ || !job_queue_.empty();
  }

  // Wait for the threads to finish.
  void Wait();

  // Queue a job.
  void QueueJob(ThreadPoolJob job);

 private:
  // Loop function for all threads.
  void Loop();

  // Number of threads.
  int num_threads_ = 1;

  // Number of waiting threads.
  int num_waiting_threads_ = 0;

  // List of threads.
  std::vector<std::thread> threads_;

  // If true, all threads should terminate.
  bool terminated_ = false;

  // Job queue.
  std::queue<ThreadPoolJob> job_queue_;

  // Mutex protecting the job queue.
  std::mutex job_queue_mutex_;

  // Condition variable for the job queue or for the signal to terminate.
  std::condition_variable job_queue_or_terminate_condition_;

  // Mutex to indicate when all threads are done.
  std::mutex done_mutex_;

  // Condition variable for indicating when all threads are done.
  std::condition_variable done_condition_;
};

}  // namespace utils
