"""
====================================================================================
Producer Consumer Problem  — Version 2: Two Conditions
====================================================================================

BoundedBuffer:
    - capacity
    - buffer (deque)
    - one shared Lock
    - two Conditions sharing the same Lock
        → producer_lock: producers wait when buffer is FULL
        → consumer_lock: consumers wait when buffer is EMPTY

Producer:
    - acquires the shared lock
    - waits while buffer is FULL
    - adds item
    - notifies ONE waiting consumer

Consumer:
    - acquires the shared lock
    - waits while buffer is EMPTY
    - removes item
    - notifies ONE waiting producer

Important:
    - Both Conditions use the SAME underlying Lock.
    - Use while, not if, when waiting.
    - Producer waits on producer_lock.
    - Consumer waits on consumer_lock.
    - After put() → notify consumer_lock.
    - After get() → notify producer_lock.

Key idea:
    The Lock protects the shared buffer.
    Conditions decide WHEN a producer/consumer should wait.

    Lock = protects shared state
    Condition = coordinates waiting threads

Why V2?
    - V1 used one Condition + notify_all().
    - V2 separates producer and consumer waiting.
    - notify() wakes only one relevant waiting thread.
    - Avoids unnecessary wakeups.
"""

from collections import deque
import threading

class BoundedBuffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self.buffer = deque()

        # ONE shared lock protects the shared buffer.
        self.lock = threading.Lock()

        # Producers wait here when the buffer is FULL.
        self.producer_lock = threading.Condition(self.lock)

        # Consumers wait here when the buffer is EMPTY.
        self.consumer_lock =  threading.Condition(self.lock)


    def put(self, item):
        with self.producer_lock:
            while len(self.buffer) == self.capacity:
                # Releases the lock while waiting.
                # Re-acquires it before continuing.
                self.producer_lock.wait()

            self.buffer.append(item)
            # An item is now available for a consumer.
            self.consumer_lock.notify()

    def get(self):
        with self.consumer_lock:
            while not self.buffer:
                 # Releases the lock while waiting.
                self.consumer_lock.wait()

            item = self.buffer.popleft()

            # A slot is now available for a producer.
            self.producer_lock.notify()

            return item

def producer(buffer):
    for i in range(10):
        buffer.put(i)
        print(f"Produced {i}")

def consumer(buffer):
    for i in range(10):
        item = buffer.get()
        print(f"Consumed: {item}")

def main():
    buffer = BoundedBuffer(3)
    t1= threading.Thread(target=producer,args=(buffer,))
    t2= threading.Thread(target=consumer,args=(buffer,))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

if __name__=="__main__":
    main()