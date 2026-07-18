'''
Association:
A relationship where two objects are connected but can exist independently.

Example:
UberDriver <----> Rider
Doctor <----> Patient

Neither object owns the other.
'''


'''
Aggregation:
A weak HAS-A relationship.

One object contains another object, but the contained object can exist independently.

Example:
Department HAS Employees
Team HAS Players

Even if Department/Team is deleted, Employees/Players can still exist.
'''

'''
Difference between Aggregation and Composition
Composition (Strong HAS-A)
Car HAS Engine/ House HAS Rooms/ Laptop HAS Keyboard

Generally, parts belong strongly to the whole.

Aggregation (Weak HAS-A)
Department HAS Employees/ Library HAS Books / Team HAS Players

The child object can exist separately.


Relationships Summary:

Manager IS-A Employee        -> Inheritance
UberDriver USES Rider        -> Association
Department HAS Employees     -> Aggregation
Car HAS Engine               -> Composition

Interface:

An interface defines a contract that specifies
what methods a class must implement.

It focuses on WHAT should be done,
not HOW it should be done.

Examples:
Payment Interface
Notification Interface

Benefits:
- Loose coupling
- Extensibility
- Polymorphism
- Better maintainability

'''

# KEYWORDS
'''
Static:
- Belongs to the class.
- Shared by all objects.
- Python equivalent: class variables and @staticmethod.

Final:
- Strictly available in Java.
- Python has typing.Final and @final only as hints.
- Not enforced at runtime.

self:
- Refers to the current object.
- Equivalent to Java's this keyword.
'''

