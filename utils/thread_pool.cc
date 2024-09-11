#include "utils/thread_pool.h"

#include <cstdbool>
#include <mutex>

namespace utils {

void ThreadPool::Start() {
  for (int i = 0; i < num_threads_; ++i) {
    threads_.emplace_back(&ThreadPool::Loop, this);
  }
}

void ThreadPool::Stop() {
  terminated_ = true;
  job_queue_or_terminate_condition_.notify_all();
  for (auto& thread : threads_) {
    thread.join();
  }
  threads_.clear();
}

void ThreadPool::Wait() {
  std::unique_lock<std::mutex> lock(done_mutex_);
  done_condition_.wait(lock, [this] { return !busy(); });
}

void ThreadPool::QueueJob(ThreadPoolJob job) {
  {
    std::unique_lock<std::mutex> lock(job_queue_mutex_);
    job_queue_.emplace(std::move(job));
  }
  job_queue_or_terminate_condition_.notify_one();
}

void ThreadPool::Loop() {
  while (true) {
    ThreadPoolJob job;
    {
      std::unique_lock<std::mutex> lock(job_queue_mutex_);
      ++num_waiting_threads_;
      if (!busy()) {
        done_condition_.notify_one();
      }
      job_queue_or_terminate_condition_.wait(
          lock, [this] { return !job_queue_.empty() || terminated_; });
      --num_waiting_threads_;
      if (terminated_) {
        return;
      }
      job = job_queue_.front();
      job_queue_.pop();
    }
    job();
  }
}

}  // namespace utils
