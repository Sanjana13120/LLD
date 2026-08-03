# ================================================================================================================================
# Strategy design pattern is a behavioural design pattern that encapsulates each algorithm into separate classes and makes the algorithm interchangable. The client can switch between different algorithms at runtime without changing the code that uses them.
#
# When to use:
# - When multiple algorithms can perform the same task.
# - When you want to avoid long if-elif-else or switch statements.
# - When algorithms may change independently from the client.
# - When following the Open/Closed Principle (add new strategies without modifying existing code).
#
# Example:
# A payment system supports multiple payment methods such as Credit Card, UPI, and PayPal. The PaymentService doesn't know how each payment works; it simply delegates the payment to the selected strategy.
#
# Components:
# 1. Strategy - Common interface for all payment methods (PaymentStrategy).
# 2. Concrete Strategies - Different payment implementations (CreditCardPayment, UPIPayment, PayPalPayment).
# 3. Context - Uses a strategy object to perform the payment (PaymentService).
# 4. Client - Chooses the appropriate strategy at runtime.
#
# ================================================================================================================================



from abc import ABC, abstractmethod

class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self,amount):
        pass

class CreditCardPayment(PaymentStrategy):
    def pay(self,amount):
        print(f"Paid {amount} using Credit Card")

class UPIPayment(PaymentStrategy):
    def pay(self,amount):
        print(f"Paid {amount} using UPI")

class PayPalPayment(PaymentStrategy):
    def pay(self,amount):
        print(f"Paid {amount} using PayPal")

class PaymentService:
    def __init__(self,strategy:PaymentStrategy):
       self.strategy=strategy

    def make_payment(self,amount):
       self.strategy.pay(amount)

if __name__=="__main__":
    payments=[CreditCardPayment(), UPIPayment(), PayPalPayment()]

    for strategy in payments:
        service=PaymentService(strategy)
        service.make_payment(500)


# Output:
# Paid 500 using Credit Card
# Paid 500 using UPI
# Paid 500 using PayPal