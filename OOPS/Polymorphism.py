'''
Polymorphism is the ability of the same method call to exhibit different behaviors depending on the object invoking it.
Same method call. Different behavior.

'''

class Animal:

    def __init__(self):
        pass

    def make_sound(self):
        pass


class Dog(Animal):
    def make_sound(self):
        print("Dog: Bark")

class Cat(Animal):
    def make_sound(self):
        print("Cat: Meow")

animals=[Dog(),Cat()]
for animal in animals:
    animal.make_sound()

'''
OP: 
Dog: Bark
Cat: Meow

animal.make_sound() -- Polymorphism 


Method Overriding:  Runtime Polymorphism
Parent and child class
Same method name, Child changes implementation

Example:

Animal → make_sound()
Dog → Bark
Cat → Meow

✅ Supported in Python.

Method Overloading: 
Same method name, Different parameters

Traditional Java-style: ❌ Not supported in Python.

Achieved using in py:

✅ Default parameters
✅ *args
'''