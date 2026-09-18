# ============================================================
# Thread Pool V2 - with Future and Callable support
# ============================================================

"""
Why Future?
Future decouples task submission from result retrieval.

Goal:
- Return a Future object from submit() so the caller can retrieve results or exceptions asynchronously.
- Allow worker threads to execute tasks and update Future states.

Components:
- Future: Represents the result of an asynchronous operation (PENDING -> DONE).
- ThreadPool: Manages worker threads and a task queue.
- Worker threads: Continuously pull (task, future) tuples, execute, and update futures.
- threading.Condition: Used inside Future so callers block (wait) until the result is ready.

Flow:
future = pool.submit(task)
    ↓
Creates Future (status=PENDING)
    ↓
queue.put((task, future))
    ↓
Worker gets (task, future)
    ↓
Executes task() inside try/except/finally
    ↓
future.update_result(result_or_exception)  [Notifies waiting threads]
    ↓
Caller calls future.get_result() -> wakes up and returns result

ThreadPool decides WHO executes the task. Future lets the caller track WHAT happened to that particular task and retrieve its result later.

"""

import threading, queue, time


class Future:
    def __init__(self):
        self.status = "PENDING"
        self.result = None
        self.condition = threading.Condition()

    def update_result(self, result):
        with self.condition:
            self.result = result
            self.status = "DONE"

            self.condition.notify()

    def get_result(self):
        with self.condition:
            while self.status == "PENDING":
                self.condition.wait()

            return self.result


class ThreadPool:
    def __init__(self, no_of_workers):
        self.queue = queue.Queue()
        self.no_of_workers = no_of_workers
        self.workers = []

        for i in range(self.no_of_workers):
            t = threading.Thread(target=self.worker)
            t.start()
            self.workers.append(t)

    def worker(self):
        while True:
            item = self.queue.get()

            if item is None:
                self.queue.task_done()
                break

            task, future = item

            try:
                result = task()
                future.update_result(result)

            except Exception as e:
                future.update_result(e)
            finally:
                self.queue.task_done()

    def submit(self, task):
        future = Future()
        self.queue.put((task, future))
        return future

    def shutdown(self):
        for _ in range(self.no_of_workers):
            self.queue.put(None)

        for t in self.workers:
            t.join()


def add(a, b):
    time.sleep(1)
    return a + b


def main():
    pool = ThreadPool(3)

    future = pool.submit(lambda: add(10, 20))
    # Check status immediately after submitting (worker might still be working)
    print("Status right after submit:", future.status)

    result = future.get_result()

    print("Status after get_result:", future.status)
    print("Final Result:", result)

    pool.queue.join()
    pool.shutdown()


if __name__ == "__main__":
    main()
