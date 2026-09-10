# ============================================================
# Thread Pool - fixed worker threads + task queue
# ============================================================

'''
Goal:  Reuse a fixed number of worker threads instead of creating a new thread for every task.


Component: 
- Worker threads
- Thread - safe queues
- submit()
- shutdown()

Flow:
submit(task)
    ↓
queue.put(task)
    ↓
worker: queue.get()
    ↓
task()
    ↓
queue.task_done()

Worker:
- continuously gets tasks and executes them
- calls task_done() in finally
- None = sentinel → worker exits

queue.Queue:
- Thread-safe FIFO queue for communication between producers/workers

queue.join():
- Waits until every queued item has task_done().

thread.join():
- Waits for a particular worker thread to terminate.

shutdown():
- Put one None per worker
- join() every worker


'''
import queue, threading

class ThreadPool:
    def __init__(self, num_of_workers):
        self.queue = queue.Queue()
        self.workers  = []
        self.num_of_workers = num_of_workers

        for _ in range(self.num_of_workers):
            t = threading.Thread(target=self.worker)
            t.start()
            self.workers.append(t)

    def worker(self):
        while True:
            task = self.queue.get()

            if task is None:
                self.queue.task_done()
                break

            try:
                task()

            finally:
                self.queue.task_done()


    def submit(self, task):
        self.queue.put(task)

    def shutdown(self):
        for _ in range(self.num_of_workers):
            self.queue.put(None)

        for t in self.workers:
            t.join()
            
def Hello():
    print("Hello")

pool = ThreadPool(3)

pool.submit(Hello)
pool.submit(Hello)
pool.submit(Hello)

pool.queue.join()

pool.shutdown()

