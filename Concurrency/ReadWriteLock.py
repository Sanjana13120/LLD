"""
ReadWriteLock

Mental model:
- Multiple readers can read simultaneously.
- Writer needs exclusive access.
- Reader and writer cannot access shared data simultaneously.

State:
- reader_count:    Number of readers currently holding the read lock.
- active_writer:   Whether a writer currently holds the write lock.
- waiting_writers: Number of writers currently waiting to acquire the write lock.

Synchronization:
- condition protects all internal state.
- condition.wait() releases the underlying lock while waiting and reacquires it before returning.
- Always use `while` when waiting because waking up does not guarantee that the condition is still true.

Writer preference:
- If a writer is waiting, new readers must wait.
- This prevents writer starvation.

Invariants:
- reader_count >= 0
- active_writer == True => reader_count == 0
- active_writer == True => only one writer is active
- waiting_writers >= 0

Lifecycle:
Reader:
    lock_read()
        -> wait while writer is active OR writer is waiting
        -> increment reader_count
    unlock_read()
        -> decrement reader_count
        -> notify waiting threads when last reader leaves

Writer:
    lock_write()
        -> wait while readers exist OR another writer is active
        -> mark active_writer = True
    unlock_write()
        -> mark active_writer = False
        -> notify waiting threads

Policy:
- This implementation favors writers over newly arriving readers.
- It does not guarantee FIFO ordering.

API contract:
- Caller must correctly pair lock/unlock calls.
- Ownership validation is not implemented in this basic version.

"""

import threading, time

class ReadWriteLock:
    def __init__(self):
        self.reader_count = 0
        self.active_writer = False
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)

        # Number of writers currently waiting to acquire the lock.
        self.waiting_writers = 0

    def lock_read(self):
        with self.condition:
            while self.active_writer or self.waiting_writers > 0:
                self.condition.wait()
            self.reader_count += 1

    def unlock_read(self):
        with self.condition:
            self.reader_count -= 1
            if self.reader_count == 0:
                self.condition.notify_all()

    def lock_write(self):
        with self.condition:
            self.waiting_writers +=1
            try:
                while self.reader_count > 0 or self.active_writer:
                    self.condition.wait()
            finally:
                self.waiting_writers -= 1
            self.active_writer = True

    def unlock_write(self):
        with self.condition:
            self.active_writer = False
            self.condition.notify_all()

if __name__=="__main__":
    rw = ReadWriteLock()

    def reader(name):
        rw.lock_read()
        print(f"{name} entered")

        time.sleep(2)

        print(f"{name} completed")
        rw.unlock_read()

    def writer(name):
        print(f"{name} trying to write")
        rw.lock_write()
        print(f"{name} entered")

        time.sleep(2)

        print(f"{name} completed")
        rw.unlock_write()

    # Test writer preference:
    # R1 reads -> W1 waits -> R2 waits -> W1 writes -> R2 reads

    t1 = threading.Thread(target=reader,args=("R1",))
    t2 = threading.Thread(target=writer, args=("W1",))

    t3 = threading.Thread(target=reader, args=("R2",))

    t1.start()
    time.sleep(0.1)
    t2.start()
    time.sleep(0.1)
    t3.start()

    t1.join()
    t2.join()
    t3.join()

    