"""
================================================================================
LLD: Notification System
================================================================================

Functional Requirements:
1. System should be able to send notification.
2. System should support multiple types of channels - sms/email/push
3. Notifies based on user's preferences.
4. Retry failed notifications
5. System should send notifications asynchronously
6. Caller need not know which channesl to use

Non - Functional Requirments:
1. Scalability: system should handle a large volume of notifications.
2. Reliability: notifications shouldn't be lost if a worker/provider temporarily fails.
3. Thread safety: relevant because multiple workers may process notifications concurrently.
4. Latency: once accepted, notification should be processed reasonably quickly.
5. Error handling: distinguish transient failures from permanent failures.
6. Atleast once delivery

Identify core entities:

User
    - userid
    - username

NotificationChannelType(Enum)
    - SMS/Email/Push

NotificationEvent(Enum)
    - ORDER_PLACED, ORDER_SHIPPED, OTP

NotificationStatus(Enum)
    - SENT/ PENDING/ FAILED

NotificationChannel --> (Strategy Design pattern)
    - sms/email/push  (inheritance) 
    + send_notification(recipient_id, message)       

UserPreferenceService
    - preferences = {userid + eventType: Set<NotificationChannelType>}

    + set_preferences()
    + get_preferences(user, event)
    
Notification
    - id, user, message, priority, status: NotificationStatus, event, deliveries}

NotificationDelivery
    - notification_id, channel, status, attempts

NotificationChannelFactory
    + get_notification_channel(notification_channel_type: NotificationChannelType )

NotificationService (orchestrator)

for async processing:

NotificationRequestQueue
    + enqueue(notification)
    + claim()
    + acknowledge(notification)

NotificationWorker
    + process()
    + run()
    + stop()

RetryPolicy
    - max_attempts
    - base_delay

    + should_retry(attempt)
    + get_retry_delay(attempt)

IdempotencyManager
    - Tracks successfully processed (notification_id, channel)
    + is_processed()
    + mark_processed()

Identify Relationship:

NotificationChannelFactory --creates--> NotificationChannel
EmailChannel/ SMSChannel/ PushChannel --is-a--> NotificationChannel

Notification ---HAS-A--> User
Notification ---HAS-A--> NotificationDelivery

NotificationService ---uses--> NotificationRequestQueue

NotificationWorker ---uses--> NotificationRequestQueue
NotificationWorker ---uses--> UserPreferenceService
NotificationWorker ---uses--> NotificationChannelFactory
NotificationWorker ---uses--> IdempotencyManager
NotificationWorker ---uses--> RetryPolicy

Key Design Decisions:

1. Strategy Pattern - Allows new notification channels to be added without changing worker logic.

2. Factory Pattern - Keeps channel creation separate from notification processing.

3. Per-channel NotificationDelivery - Each channel has independent status and retry attempts.

4. Idempotency - Tracked using (notification_id, channel) so duplicate processing does not resend an already successful delivery.

5. Priority Queue -Lower priority value means higher urgency.

6. At-least-once processing - Notification is claimed and tracked as inflight until acknowledged. In production, an unacknowledged notification would be requeued after a visibility timeout / lease expiry.

7. Retry - Failed deliveries are retried using exponential backoff. Current implementation uses sleep() for simplicity. In production, retries could be scheduled through a delayed queue.

Coding
"""

from queue import PriorityQueue, Empty
from abc  import ABC, abstractmethod
from enum import Enum, auto
import threading, time, itertools

class NotificationStatus(Enum):
    SENT = auto()
    FAILED = auto()
    PENDING = auto()

class NotificationChannelType(Enum):
    SMS = auto()
    EMAIL = auto()
    PUSH = auto()

class NotificationEvent(Enum):
    ORDER_PLACED = auto()
    ORDER_SHIPPED = auto()
    ORDER_DELIVERED = auto()
    OTP = auto()

class User:
    def __init__(self, user_id, user_name):
        self.user_id = user_id
        self.user_name = user_name

class Notification:
    def __init__(self, id, user, message, priority, event: NotificationEvent):
        self.id = id
        self.user = user
        self.message = message
        self.priority = priority
        self.status = NotificationStatus.PENDING
        self.event = event
        self.deliveries = {}

class NotificationDelivery:
    def __init__(self, notification_id, channel: NotificationChannelType, status: NotificationStatus):
        self.channel = channel
        self.status = status
        self.notification_id = notification_id
        self.attempts = 0            

class NotificationChannel(ABC):
    @abstractmethod
    def send_notification(self, recipient_id, message):
        pass

class SMSNotificationChannel(NotificationChannel):
    def send_notification(self, recipient_id, message):
        print(f"[SMS] Hi {recipient_id}, {message}")
        return True

class EMailNotificationChannel(NotificationChannel):
    def send_notification(self, recipient_id, message):
        print(f"[EMAIL] Hi {recipient_id}, {message}")
        return True

class PushNotificationChannel(NotificationChannel):
    def send_notification(self, recipient_id, message):
        print(f"[Push] Hi {recipient_id}, {message}")
        return True
    
class NotificationChannelFactory:
    def get_notification_channel(self, notification_channel_type: NotificationChannelType):
        if notification_channel_type == NotificationChannelType.EMAIL:
            return EMailNotificationChannel()

        elif notification_channel_type == NotificationChannelType.SMS:
            return SMSNotificationChannel()

        elif notification_channel_type == NotificationChannelType.PUSH:
            return PushNotificationChannel()

        else:
            raise ValueError("Invalid Notification channel type")

class NotificationRequestQueue:
    def __init__(self):
        self.queue = PriorityQueue()
        self.inflight = {}

        # Tie-breaker so PriorityQueue never compares Notification objects when two notifications have the same priority.
        self.counter = itertools.count()
        self.lock = threading.Lock()

    def enqueue(self, notification: Notification):
        # Lower priority value means higher urgency.
        self.queue.put((notification.priority, next(self.counter),notification))

    def claim(self):
        try:
            _, _ ,notification = self.queue.get_nowait()
        except Empty:
            return None

        with self.lock:
            self.inflight[notification.id] = notification

        return notification

    def acknowledge(self, notification: Notification):
        with self.lock:
            self.inflight.pop(notification.id,None)

class IdempotencyManager:
    def __init__(self):
        self.processed = set()
        self.lock = threading.Lock()

    def is_processed(self, notification_id, channel_type):
        with self.lock:
            # Idempotency is tracked per notification + channel.
            # Email success should not prevent SMS delivery.
            return (notification_id, channel_type) in self.processed

    def mark_processed(self, delivery: NotificationDelivery):
        with self.lock:
            self.processed.add((delivery.notification_id, delivery.channel))

class UserPreferences:
    def __init__(self):
        self.preferences = {}

    def set_preferences(self, user_id, event, channel_types: set[NotificationChannelType]):
        self.preferences[(user_id,event)] = channel_types

    def get_preferences(self, user_id, event):
        return self.preferences.get((user_id,event), set())

class RetryPolicy:
    def __init__(self, max_attempts, base_delay):
        self.max_attempts = max_attempts
        self.base_delay = base_delay

    def should_retry(self, attempt):
        return attempt < self.max_attempts

    def get_retry_delay(self, attempt):
        # Exponential backoff: 1s, 2s, 4s, ...
        return self.base_delay * (2**(attempt-1))


class NotificationWorker:
    def __init__(self,  queue: NotificationRequestQueue, channel_factory: NotificationChannelFactory, user_preferences : UserPreferences, idempotency_manager : IdempotencyManager, retry_policy: RetryPolicy):
        self.queue = queue
        self.channel_factory = channel_factory
        self.user_preferences = user_preferences
        self.idempotency_manager = idempotency_manager
        self.retry_policy = retry_policy

        self.running = True

    def process(self):
        claimed_notification  = self.queue.claim()
        if claimed_notification is None:
            return None

        channels = self.user_preferences.get_preferences(claimed_notification.user.user_id, claimed_notification.event)

        # Each selected channel has independent delivery state and retry lifecycle.
        for channel in channels:
            if self.idempotency_manager.is_processed(claimed_notification.id, channel):
                continue

            delivery = claimed_notification.deliveries.get(channel)

            if delivery is None:
                delivery = NotificationDelivery(claimed_notification.id, channel, NotificationStatus.PENDING)
                claimed_notification.deliveries[channel] = delivery

            notification_channel  = self.channel_factory.get_notification_channel(channel)

            while self.retry_policy.should_retry(delivery.attempts):
                delivery.attempts +=1
                result = notification_channel.send_notification(claimed_notification.user.user_id, claimed_notification.message)

                if result:
                    delivery.status = NotificationStatus.SENT
                    self.idempotency_manager.mark_processed(delivery)
                    break

                else:
                    if delivery.attempts < self.retry_policy.max_attempts:
                        delay = self.retry_policy.get_retry_delay(delivery.attempts)
                        time.sleep(delay)

            if delivery.status != NotificationStatus.SENT:
                delivery.status = NotificationStatus.FAILED

        if not claimed_notification.deliveries:
            claimed_notification.status = NotificationStatus.FAILED
        elif all(delivery.status == NotificationStatus.SENT for delivery in claimed_notification.deliveries.values()):
            claimed_notification.status = NotificationStatus.SENT
        else:
            claimed_notification.status = NotificationStatus.FAILED


        self.queue.acknowledge(claimed_notification)

    def run(self):
        while self.running:
            result = self.process()

            if result is None:
                time.sleep(0.1)

    def stop(self):
        self.running = False
        

class NotificationService:
    def __init__(self, queue):
        self.queue = queue

    def submit_request(self, notification: Notification):
        self.queue.enqueue(notification)
        
if __name__ == "__main__":
    queue = NotificationRequestQueue()
    notification_service = NotificationService(queue)
    user_preference= UserPreferences()
    idempotency_manager = IdempotencyManager()
    channel_factory = NotificationChannelFactory()

    retry_policy = RetryPolicy(max_attempts=3, base_delay=1)

    user1 = User("U1", "Sanjana")
    user_preference.set_preferences(user1.user_id, NotificationEvent.ORDER_PLACED,{NotificationChannelType.EMAIL, NotificationChannelType.SMS})

    user_preference.set_preferences(user1.user_id, NotificationEvent.OTP, {NotificationChannelType.SMS})

    worker = NotificationWorker(queue,channel_factory, user_preference, idempotency_manager, retry_policy)

    worker_thread = threading.Thread(target=worker.run)
    worker_thread.start()

    notification1 = Notification("N1",user1, "Your order has shipped",1,NotificationEvent.ORDER_PLACED)
    notification2 = Notification("N2",user1, "OTP: 1234",0,NotificationEvent.OTP)

    notification_service.submit_request(notification1)
    notification_service.submit_request(notification2)

    # Duplicate submission should not result in duplicate delivery
    # notification_service.submit_request(notification2)

    time.sleep(5)
    worker.stop()
    worker_thread.join()

        
