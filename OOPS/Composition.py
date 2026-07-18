'''
Composition represents a HAS-A relationship.

'''
class Engine:
    def start(self):
        print("Engine is starting")

class ElectricEngine:
    def start(self):
        print("Electric engine is starting")

class Car:
    def __init__(self,engine):
        self.engine=engine

    def start_car(self):
        self.engine.start()

car1=Car(Engine())
car2=Car(ElectricEngine())
car1.start_car()
car2.start_car()

'''
Output:
Engine is starting
Electric engine is starting

'''