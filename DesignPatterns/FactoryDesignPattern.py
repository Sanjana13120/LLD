# ==============================================================================================================================================
# Factory Design pattern is a Creational Design Pattern that encapsulates object creation in a separate factory class. Instead of 
# directly using constructors, clients request the Factory to create and return the appropriate object.

# The client depends on the Factory instead of directly creating concrete objects.

# When to use?
# - When the client should not know which concrete class is being instantiated.
# - When object creation logic is complex or may change in the future.
# - When you want to centralize object creation in one place.

# Limitation:
# - A basic Factory using if-else still violates the Open-Closed Principle (OCP) because adding a new type requires modifying the Factory.
# - This can be improved using a registry-based Factory, reflection, or dependency injection frameworks.
# ==============================================================================================================================================

from abc import ABC, abstractmethod

class Notification(ABC):
    @abstractmethod
    def send(self,message:str):
        pass

class EmailNotification(Notification):
    def send(self,message: str):
        print(f"Sending Email: {message}")

class SMSNotification(Notification):
    def send(self,message: str):
        print(f"Sending SMS: {message}")

class NotificationServiceWithoutFactory:
# Here we have two responsibilities: # 1. Creating the object  2. Sending the notification. This violates SRP.
# If a new notification type (e.g., WhatsApp) is added, this class must also be modified, violating OCP.
    def send_service(self,notification_type:str, message:str):
        if notification_type=="Email":
            email=EmailNotification()
            email.send(message)
        elif notification_type=="SMS":
            sms=SMSNotification()
            sms.send(message)
        else:
            raise ValueError("Invalid Notification type")


class NotificationFactory:
    @staticmethod
    def create_notification(notification_type):
        if notification_type=="Email":
            return EmailNotification()
        elif notification_type=="SMS":
            return SMSNotification()
        else:
            raise ValueError("Invalid Notification type")

class NotificationServiceWithFactory:
   def send_service(self,notification_type:str, message:str):
       notification = NotificationFactory.create_notification(notification_type)
       notification.send(message)

if __name__=="__main__":
    service = NotificationServiceWithFactory()
    service.send_service("Email", "Welcome to LLD learning class")

    service.send_service("SMS", "Hi, your otp is 12345")

    try:
        service.send_service("Whatsapp", "Hey dude") 
    except ValueError as e:
        print(e)


# Real-world examples:
# - Payment Gateway Factory (Stripe, Razorpay, PayPal)
# - Notification Factory (Email, SMS, Push)
# - Database Factory (MySQL, PostgreSQL, MongoDB)