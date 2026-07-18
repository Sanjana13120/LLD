'''
class  -> Blueprint for objects
object -> Instance of class

'''


class Employee:
    def __init__(self,name,salary):
        self.name=name
        self.salary=salary
    
    def display(self):
        print(f"Name: {self.name}")
        print(f"Salary: {self.salary}")



emp=Employee("Sanjana",1000)
emp.display()