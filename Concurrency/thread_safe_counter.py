# ============================================================
# THREAD-SAFE COUNTER
# ============================================================
#
# Thread(target=worker) → create thread
# start()               → run thread
# join()                → wait for thread
# Lock                  → protect shared data
#
# 2 threads × 1000 increments = 2000


import threading


class ThreadSafeCounter:
    def __init__(self):
        self.value = 0
        self.lock = threading.Lock()

    def increment(self):
        with self.lock:
            self.value += 1

    def decrement(self):
        with self.lock:
            self.value -= 1

    def get(self):
        with self.lock:
            return self.value

def worker():
    for _ in range(1000):
        counter.increment()


if __name__ == "__main__":
    counter = ThreadSafeCounter()

    t1 = threading.Thread(target=worker)
    t2 = threading.Thread(target=worker)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    print(f"Final counter value: {counter.get()}")