"""
====================================================================================
Producer Consumer Problem - V1: Single Condition
====================================================================================


BoundedBuffer:
    - capacity
    - buffer (deque)
    - one shared Condition
    - Condition protects access to the shared buffer

Producer:
    - waits while buffer is FULL
    - adds item
    - notifies waiting consumers

Consumer:
    - waits while buffer is EMPTY
    - removes item
    - notifies waiting producers

Important:
    - Use while, not if, when waiting.
    - wait() releases the lock while waiting and reacquires it before returning.
    - notify_all() wakes all waiting threads, but they must reacquire the lock
      and re-check the condition.
    - Print order is NOT guaranteed because thread scheduling is nondeterministic.

V1 limitation:
    - Both producers and consumers use the same Condition.
    - notify_all() can wake threads that cannot proceed.
    - Example: one free slot → waking 5 waiting producers is unnecessary.

V2 improvement:
    - One shared Lock
    - Two Conditions using the same Lock
        → producer condition: waits for space
        → consumer condition: waits for items
    - notify() can wake one relevant waiting thread.

"""

from collections import deque
import threading, time

class BoundedBuffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self.buffer = deque()
        self.condition = threading.Condition()

    def put(self, item):
        with self.condition:

            while len(self.buffer) == self.capacity:
                self.condition.wait()

            self.buffer.append(item)

            self.condition.notify_all()

    def get(self):
        with self.condition:
            while not self.buffer:
                self.condition.wait()

            item = self.buffer.popleft()

            self.condition.notify_all()

            return item

def producer(buffer):
    for i in range(20):
        buffer.put(i)
        print(f"Produced {i}")

def consumer(buffer):
    for i in range(20):
        item = buffer.get()
        print(f"Consumed: {item}")
        time.sleep(1)

def main():

    buffer = BoundedBuffer(3)

    t1= threading.Thread(target=producer, args= (buffer,))
    t2= threading.Thread(target=consumer, args= (buffer,))

    t3= threading.Thread(target=producer, args= (buffer,))
    t4 = threading.Thread(target=consumer, args= (buffer,))

    t1.start()
    t2.start()

    t3.start()
    t4.start()

    t1.join()
    t2.join()

    t3.join()
    t4.join()

if __name__ == "__main__":
    main()