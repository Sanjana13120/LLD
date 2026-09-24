# ============================================================
# CONCURRENCY BASICS
# ============================================================

# Key concepts:
# - Thread: unit of execution within a process
# - start(): starts a new thread
# - join(): waits for a thread to finish
#
# - Race Condition: Multiple threads access shared state and result depends on timing.
#
# - Critical Section:  Code that accesses/modifies shared state and must be protected.
#
# - Lock / Mutex:  Allows only one thread at a time into the critical section.
#
# - Keep critical section small:  Lock only what needs protection to reduce contention.
#
# - GIL (CPython):  Interpreter-level mechanism; NOT a replacement for application locks.

# ============================================================
# 1. Lock / Mutex - Protecting a shared counter
# ============================================================
# Interview takeaway: Don't assume GIL makes shared-state operations thread-safe. Use an explicit Lock when multiple threads modify shared state.

import threading, time


class LockDemo:
    def __init__(self):
        self.lock = threading.Lock()
        self.counter = 0

    def demo(self):
        for i in range(1000):
            with self.lock:
                self.counter += 1


# ============================================================
# 2. RLock / Reentrant Lock:
# ============================================================
# - Same thread can acquire the lock multiple times.
# - RLock tracks the owning thread and acquisition count.
# - Every acquire() must have a matching release().
# - Useful when a locked method calls another method that needs the same lock.
# - Prevents self-deadlock in such cases
# - "Lock cannot be acquired twice by the same thread, so doing so can cause self-deadlock. RLock allows the owning thread to acquire it multiple times and keeps an acquisition count."


class Account:
    def __init__(self):
        self.rlock = threading.RLock()

    def withdraw(self):
        with self.rlock:
            self.validate()

    def validate(self):
        with self.rlock:
            print("Validated")


# ============================================================
# 3. Condition Variable
# ============================================================
# Purpose:
# - Used when a thread needs to WAIT until some condition becomes true.
# - Common example: Producer-Consumer.
#
# Created with a lock:
#     lock = threading.RLock()
#     condition = threading.Condition(lock)
#
# Basic pattern:
#
#     with condition:
#         while condition_not_met:
#             condition.wait()
#
#         # do work
#
#         condition.notify()
#
# wait():
# - Puts the current thread to sleep.
# - Releases the underlying lock while waiting.
# - Re-acquires the lock before wait() returns.
#
# notify():
# - Wakes one waiting thread.
#
# notify_all():
# - Wakes all waiting threads.
#
# Important:
# - Use while, NOT if, around wait().
# - After waking up, always check the condition again.
#
# Interview mental model:
# - Lock      -> "Who can access the shared resource?"
# - Condition -> "When can I proceed?"
#
# Condition is used WITH a lock; it doesn't replace the lock.

# ============================================================
# 4. Semaphores
# ============================================================
# - Limits how many threads can access a resource at once.
# - Semaphore(3) -> max 3 threads at a time.
# - 4th thread calling acquire() -> waits until a permit is released.
# - acquire() -> take permit
# - release() -> return permit
#
# Lock      -> max 1 thread
# Semaphore -> max N threads
#
# Common use:
# - Limit DB connections / API calls / resource access.


class SemaphoreDemo:
    def __init__(self):
        self.semaphore = threading.Semaphore(3)

    def worker(self):
        with self.semaphore:
            print("Using resource")
            time.sleep(2)


# ============================================================
# 5. Deadlock
# ============================================================
# - Two or more threads wait indefinitely for resources/locks held by each other.
#
# Example:
#   W1: holds A → waits for B
#   W2: holds B → waits for A
#
# Deadlock requires ALL 4:
# 1. Mutual Exclusion - Only one thread can hold a resource/lock at a time.
# 2. Hold and Wait    - A thread holds one resource while waiting for another.
# 3. No Preemption    - A resource cannot be forcibly taken; it must be released by the holder.
# 4. Circular Wait    - Threads form a cycle where each waits for a resource held by another.
#
# Prevention:
# - Consistent lock ordering → prevents Circular Wait.
#   Example: Always acquire A → B → C.
# - Avoid holding one lock while waiting for another when possible.
# - Use lock timeouts when appropriate.
#
# Key idea:
# - Conditions = why deadlock can happen.
# - Prevention = how we avoid/break those conditions.


# ============================================================
# Ordered Execution using Semaphores
# ============================================================
# Goal:
# - Multiple threads may start in any order.
# - But execution must happen in a fixed order: A → B → C.
#
# Semaphore is used as a "permission/token" here.
#
# Initial state:
# - A = 1 → A can proceed
# - B = 0 → B must wait
# - C = 0 → C must wait
#
# Flow:
#   A acquires A → executes → releases B
#   B acquires B → executes → releases C
#   C acquires C → executes
#
# Important:
# - Here Semaphore is being used for coordination/order,
#   not just for limiting the number of concurrent threads.

class OrderedExecution:
    def __init__(self):
        self.a = threading.Semaphore(1)
        self.b = threading.Semaphore(0)
        self.c = threading.Semaphore(0)

    def execute_a(self):
        self.a.acquire()
        print("A")
        self.b.release()

    def execute_b(self):
        self.b.acquire()
        print("B")
        self.c.release()

    def execute_c(self):
        self.c.acquire()
        print("C")


# ============================================================
# MAIN
# ============================================================


def main():
    # lock
    lock_demo = LockDemo()
    threads = []

    for i in range(1, 6):
        t = threading.Thread(target=lock_demo.demo)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print("Final counter:", lock_demo.counter)

    # rlock

    rlock_demo = Account()

    t1 = threading.Thread(target=rlock_demo.withdraw)
    t1.start()
    t1.join()

    # semaphore
    semaphore_demo = SemaphoreDemo()
    threads_semaphore = []
    for i in range(5):
        t = threading.Thread(target=semaphore_demo.worker)
        t.start()
        threads_semaphore.append(t)

    for t in threads_semaphore:
        t.join()

    # ordered execution

    print("\n--- Ordered Execution ---")

    ordered = OrderedExecution()

    t1 = threading.Thread(target=ordered.execute_b)
    t2 = threading.Thread(target=ordered.execute_c)
    t3 = threading.Thread(target=ordered.execute_a)

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()
        

if __name__ == "__main__":
    main()
