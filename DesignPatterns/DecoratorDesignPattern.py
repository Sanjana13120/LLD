# ================================================================================================================================
# Decorator Design Pattern is a a structural design pattern that allows behavior to be added to an object dynamically
# without modifying its original class.
#
# Instead of creating many subclasses for every possible combination of features, decorators wrap the original object and extend # its functionality.
#
# When to use:
# - When we need to add responsibilities to objects dynamically at runtime.
# - When subclassing would create too many classes (class explosion).
# - When we want to follow the Open/Closed Principle (open for extension, closed for modification).
# - When features can be combined in different ways.
#
# Example:
# A coffee shop allows customers to customize coffee:
# - Basic coffee
# - Coffee + Milk
# - Coffee + Sugar
# - Coffee + Milk + Sugar
#
# Instead of creating separate classes:
# CoffeeWithMilk, CoffeeWithSugar, CoffeeWithMilkAndSugar... we wrap the coffee object with decorators.
#
# Components:
#
# 1. Component Interface:
#    Defines the common interface for the object and decorators.
#    Example: CoffeeComponent
#
# 2. Concrete Component:
#    The original object whose behavior can be extended.
#    Example: Coffee
#
# 3. Base Decorator:
#    Maintains a reference to the wrapped component and delegates operations to it.
#    Example: Decorator
#
# 4. Concrete Decorators:
#    Add new behavior before/after delegating to the wrapped object.
#    Example: Milk, Sugar
#
# ================================================================================================================================


from abc import ABC, abstractmethod

class CoffeeComponent(ABC):
    @abstractmethod
    def calculate_cost(self):
        pass

class Coffee(CoffeeComponent):
    def __init__(self):
        self.cost=100

    def calculate_cost(self):
        return self.cost
    
class Decorator(CoffeeComponent, ABC):
    def __init__(self,wrapped_object: CoffeeComponent):
        self.wrapped_object=wrapped_object 

class Milk(Decorator):
    def __init__(self, wrapped_object):
        super().__init__(wrapped_object)
        self.extra_cost=20

    def calculate_cost(self):
        return self.wrapped_object.calculate_cost() + self.extra_cost

class Sugar(Decorator):
    def __init__(self, wrapped_object):
        super().__init__(wrapped_object)
        self.extra_cost=10

    def calculate_cost(self):
        return self.wrapped_object.calculate_cost() + self.extra_cost
        

if __name__=="__main__":
    total =  Milk(Sugar(Coffee()))
    print(f"Total cost = {total.calculate_cost()}")
    