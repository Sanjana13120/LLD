# Observer Design Pattern is a behavioural design pattern that defines a one-to-many dependency between objects. When the state of one object (Subject) changes, all its dependent objects (Observers) are automatically notified and updated.
#
# When to use:
# - When multiple objects need to be notified about changes in another object.
# - When you want loose coupling between the publisher and subscribers.
# - When observers can be added or removed dynamically at runtime.
# - When implementing event-driven systems such as notifications or listeners.
#
# Example:
# A YouTube channel uploads a new video. All subscribed users automatically receive a notification without the channel needing to know anything about the subscribers except that they implement the Observer interface.
#
# Components:
# 1. Observer - Common interface for all subscribers (Observer).
# 2. Concrete Observer - Implements the notification behavior (Subscriber).
# 3. Subject - Interface for managing observers (Subject).
# 4. Concrete Subject - Maintains the observer list and sends notifications when its state changes (YoutubeChannel).
# 5. Client - Creates the subject and observers, subscribes them, and triggers state changes (main function).
#
# ================================================================================================================================

from abc import ABC, abstractmethod

# Observer interface: every subscriber must implement notify()
class Observer(ABC):
    @abstractmethod
    def notify(self,video):
        pass

# Concrete Observer: YouTube subscriber
class Subscriber(Observer):
    def __init__(self,name):
        self.name=name

    # Called automatically when the channel uploads a video
    def notify(self, video):
        print(f"{self.name}: received notification: {video}")

# Subject interface: defines methods for managing observers
class Subject(ABC):
    @abstractmethod
    def attach(self,observer):
        pass
    def detach(self,observer):
        pass
    def notify(self):
        pass

# Concrete Subject: YouTube channel
class YoutubeChannel(Subject):
    def __init__(self,name):
        self.name=name
        self.observers=[]
        self.latest_video=""

    # Register a new subscriber
    def attach(self,obs:Observer):
        self.observers.append(obs)

    # Remove an existing subscriber
    def detach(self, obs: Observer):
        self.observers.remove(obs)

    # Upload a new video and notify all subscribers
    def upload_video(self,video):
            self.latest_video=video
            self.notify()

    # Notify every subscribed observer
    def notify(self):
        for observer in self.observers:
            observer.notify(self.latest_video)

# Client code
if __name__=="__main__":
    channel=YoutubeChannel("CodeWithSanjana")

    subscriber1=Subscriber("Sanjana")
    subscriber2=Subscriber("Shanthi")

    channel.attach(subscriber1)
    channel.attach(subscriber2)

    channel.upload_video("How to learn LLD")  # Uploading a video triggers notifications to all subscribers
 
# Output:
# Sanjana: received notification: How to learn LLD
# Shanthi: received notification: How to learn LLD