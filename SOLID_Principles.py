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
# 4. INTERFACE SEGREGATION PRINCIPLE (ISP)
# =======================

# A class should not be forced to implement methods that it does not need.

# BAD: Fat interface
class BadWorker(ABC):
    @abstractmethod
    def work(self):
        pass

    @abstractmethod
    def eat(self):
        pass

class BadHumanWorker(BadWorker):
    def work(self):
        print("Human is working")
    
    def eat(self):
        print("Human is eating")

class BadRobotWorker(BadWorker):
    def work(self):
        print("Robot is working")
    
    def eat(self):
        raise Exception("Robot cannot eat")

# GOOD: Split interfaces
class Workable(ABC):
    @abstractmethod
    def work(self):
        pass

class Eatable(ABC):
    @abstractmethod
    def eat():
        pass

class Human(Workable,Eatable):
    def work(self):
        print("Human is working")
    
    def eat(self):
        print("Human is eating")

class Robot(Workable):
    def work(self):
        print("Robot is working")
     
# =======================
# 5. DEPENDENCY INVERSION PRINCIPLE (DIP)
# =======================

# High-level modules should not depend on low-level modules. Both should depend on abstractions.

#Dependencies should be injected from outside. ~ Dependency Injection

# BAD: Tight coupling

class BadKeyboard:
    def type(self):
        print("Typing with Keyboard")

class BadComputer:
    def __init__(self):
        self.keyboard=BadKeyboard()

    def start(self):
        self.keyboard.type()
 
# GOOD: Depend on abstraction --> Computer depends on the Keyboard abstraction instead of depending directly on MechanicalKeyboard
# or WirelessKeyboard. New keyboards can be added without modifying the Computer class.

class Keyboard(ABC):
    @abstractmethod
    def type(self):
        pass

class MechanicalKeyboard(Keyboard):
    def type(self):
        print("Typing with mechanical keyboard")

class WirelessKeyboard(Keyboard):
    def type(self):
        print("Typing with wireless keyboard")

class Computer:
    def __init__(self,keyboard:Keyboard):
        self.keyboard=keyboard
    
    def start(self):
        self.keyboard.type()
        

# ============================
# MAIN (TESTING)
# ============================

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

    #ISP 
    human=Human()
    human.work()
    human.eat()

    robot=Robot()
    robot.work()

    #DIP
    computer1= Computer(MechanicalKeyboard())
    computer1.start()

    computer2= Computer(WirelessKeyboard())
    computer2.start()

    

    