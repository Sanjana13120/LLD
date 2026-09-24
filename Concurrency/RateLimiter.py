# ============================================================
# Fixed Window Rate Limiter
# ============================================================
# Goal: Allow at most N requests within a fixed time window.
#
# Example:
#   limit = 5
#   window = 10 seconds
#
#   First 5 requests → allowed
#   6th request       → rejected
#
# State:
# - limit        → maximum requests allowed
# - window_size  → duration of each window
# - count        → requests used in current window
# - window_start → start of current window
#
# Flow:
#   request
#      ↓
#   acquire lock
#      ↓
#   window expired?
#      ├── yes → reset count + window_start
#      └── no
#      ↓
#   count < limit?
#      ├── yes → count += 1 → allow
#      └── no  → reject
#
# Concurrency:
# - check + increment must be protected by the SAME lock.
# - Locking only count += 1 is not enough.
#
# Important:
# - Fixed Window is simple but has a boundary/burst issue.
# - Example: 5 requests at the end of one window +
#            5 requests at the start of the next window
#            can happen very close together.
#
# Interview takeaway:
# "A Fixed Window Rate Limiter maintains a request count for a time window. The check-and-increment operation is protected
# by a lock so concurrent threads cannot exceed the limit."


from datetime import datetime, timedelta
import threading, time


class RateLimiter:
    def __init__(self, limit, window_size):
        self.limit = limit
        self.window_size = timedelta(seconds=window_size)
        self.count = 0
        self.window_start = datetime.now()
        self.lock = threading.Lock()

    def allow_request(self):
        with self.lock:
            # check/reset
            # check limit
            # increment
            now = datetime.now()
            window_end = self.window_start + self.window_size
            if now >= window_end:
                self.count = 0
                self.window_start = now

            if self.count < self.limit:
                self.count += 1
                print("True")
                return True
            else:
                print("False")
                return False


if __name__ == "__main__":
    rate_limiter = RateLimiter(5, 10)

    threads = []
    for _ in range(20):
        t = threading.Thread(target=rate_limiter.allow_request)
        threads.append(t)

    for t in threads:
        t.start()
        time.sleep(1)

    for t in threads:
        t.join()
