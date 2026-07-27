# ================================================================================================================================
# Abstract factory is a creational design pattern that provides an interface for creating families of related objects without
# specifying concrete classes

# The client depends only on the Abstract Factory and never knows which concrete product family is being used.

# When to use?
# - When the system needs to create families of related objects.
# - When products belonging to the same family should always be used together.
# - When switching between different product families should be easy.

# Factory pattern  - creates one object
# Abstract factory - creates a FAMILY of related objects

# =================================================================================================================================

from abc import ABC, abstractmethod

class EmailNotification(ABC):
    @abstractmethod
    def send(self,message:str):
        pass

class SMSNotification(ABC):
    @abstractmethod
    def send(self,message:str):
        pass

class GmailEmailNotification(EmailNotification):
    def send(self,message:str):
        print(f"Gmail Email: {message}")

class OutlookEmailNotification(EmailNotification):
    def send(self,message:str):
        print(f"Outlook Email: {message}")

class GmailSMSNotification(SMSNotification):
    def send(self,message:str):
        print(f"Gmail SMS: {message}")

class TeamsSMSNotification(SMSNotification):
    def send(self,message:str):
        print(f"Teams SMS: {message}")

class NotificationProviderFactory(ABC):
    @abstractmethod
    def create_email_notification(self):
        pass

    @abstractmethod
    def create_sms_notification(self):
            pass

class GoogleNotificationFactory(NotificationProviderFactory):
    def create_email_notification(self):
        return GmailEmailNotification()

    def create_sms_notification(self):
        return GmailSMSNotification()

class MicrosoftNotificationFactory(NotificationProviderFactory):
    def create_email_notification(self):
        return OutlookEmailNotification()

    def create_sms_notification(self):
        return TeamsSMSNotification()

class NotificationService:
    @staticmethod
    def send_notification_provider(factory: NotificationProviderFactory, message:str):
        email = factory.create_email_notification()
        sms = factory.create_sms_notification()

        email.send(message)
        sms.send(message)

if __name__=="__main__":
    google_factory = GoogleNotificationFactory()
    microsoft_factory = MicrosoftNotificationFactory()

    NotificationService.send_notification_provider(google_factory,"This is a Google notification")

    NotificationService.send_notification_provider(microsoft_factory,"This is a Microsoft notifications")

# Real-world examples:
# - GUI Toolkit (Windows UI, macOS UI)
# - Notification Providers (Google, Microsoft)
# - Cloud Providers (AWS, Azure, GCP)