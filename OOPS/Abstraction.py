#Abstraction means hiding implementation details and exposing only the essential behavior.

from abc import ABC, abstractmethod

class Payment(ABC):
    @abstractmethod
    def pay(self):
        pass

class CardPayment(Payment):
    def pay(self):
        print("Card payment")

class UPIPayment(Payment):
    def pay(self):
        print("UPI payment")

payments= [CardPayment(),UPIPayment()]
for payment in payments:
    payment.pay()

'''
Output:
Card payment
UPI payment
'''