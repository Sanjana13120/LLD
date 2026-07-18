''' Inheritance represents a IS-A relationship.

Inheritance is an OOP concept where one class (child/subclass) acquires the properties and methods of another class (parent/superclass).
Inheritance allows code reuse by enabling a child class to inherit attributes and methods from a parent class.

'''

from abc import ABC, abstractmethod

class Vehicle(ABC):
    def __init__(self,brand):
        self.brand=brand
    def start(self):
        print(f"{self.brand} vehicle is starting")

class Car(Vehicle):
    pass

class Bike(Vehicle):
    pass


#creating objects

car=Car("BMW")
bike=Bike("Royal Enfield")

car.start()
bike.start()

'''
O/P
BMW vehicle is starting
Royal Enfield vehicle is starting
'''