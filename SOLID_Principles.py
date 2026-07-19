from abc import ABC, abstractmethod

#  =======================
# 1. SINGLE RESPONSIBILITY PRINCIPLE (SRP)
#  =======================

# A class should have only one responsibility or one reason to change.

# Benefits:
# - Easier maintenance
# - Better readability
# - Easier testing
# - Lower coupling

#Bad Example: Violates SRP because the class has multiple responsibilities.

class BadUser:
    def __init__(self,name:str=""):
        self.name=name
    def login(self):
        print("User Logged In")

    def send_email(self):
        print("Email sent")
        
    def generate_report(self):
        print("Report generated")

#Good Example:

class User:
    def __init__(self,name:str=""):
        self.name=name

class UserLoginService:
    def login(self,user:User):
        print(f"{user.name} Logged In")

class EmailService:
    def send_email(self,user:User):
        print(f"Email sent to {user.name}")

class ReportService:
    def generate_report(self,user:User):
        print(f"Report generated for {user.name}")

# =======================
# 2. OPEN CLOSED PRINCIPLE (OCP)
# =======================

# Software entities should be open for extension but closed for modification.
# New functionality should be added by creating new classes rather than modifying existing code.


# BAD: Need to modify class for new types
class BadPayment():
    def pay(self, payment_type):
        if payment_type=="Card":
            print("Card Payment")
        elif payment_type=="UPI":
            print("UPI Payment")
        else:
            print("No Payment")

# GOOD: Extend without modifying
class Payment(ABC):
    @abstractmethod
    def pay(self):
        pass

class CardPayment(Payment):
    def pay(self):
        print("Card Payment")

class UPIPayment(Payment):
    def pay(self):
        print("UPI Payment")

# =======================
# 3. LISKOV SUBSTITUTION PRINCIPLE (LSP)
# =======================

# Objects of a child class should be able to replace objects of the parent class without 
# breaking the program.
# In simple words, Child should behave like Parent.

# BAD: Violates substitution
class BadBird:
    def fly(self):
        print("Flying")

class BadPenguin(BadBird):
    def fly(self):
        raise Exception("Cannot Fly")

#Good: Follows LSP
class Bird():
    pass

class FlyingBird(Bird, ABC):
    @abstractmethod
    def fly(self):
        pass

class Sparrow(FlyingBird):
    def fly(self):
        print("Flying")

class Penguin(Bird):
    pass


# =======================
# MAIN (TESTING)
# =======================

if __name__=="__main__":
    #SRP
    user= User("Sanjana")
    login_service=UserLoginService()
    email_service=EmailService()
    report_service=ReportService()

    login_service.login(user)
    email_service.send_email(user)
    report_service.generate_report(user)

    # OCP

    payments= [CardPayment(), UPIPayment()]
    for payment in payments:
        payment.pay()
    
    # LSP Bad Test
    try:
        bad_bird = BadPenguin()
        bad_bird.fly()   # Raises Exception
    except Exception as e:
        print(e)
    #LSP good
    bird: FlyingBird = Sparrow()
    bird.fly() 

    