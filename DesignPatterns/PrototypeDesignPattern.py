# ================================================================================================================================
# Prototype Design Pattern is a Creational Design Pattern that creates new objects by cloning an existing object instead of creating them from scratch.
#
# When to use:
# - When object creation is expensive or time-consuming.
# - When many objects share similar state.
# - When cloning is easier than constructing a new object.
#
# Shallow Copy: return copy.copy(self)
# - Suitable when the object contains only primitive/immutable fields such as int, float, bool, str, tuple
# - Copies only the outer object.
# - Nested mutable objects (lists, dictionaries, etc.) are shared.
#
# Deep Copy: return copy.deepcopy(self)
# - Suitable when the object contains nested mutable objects such as lists, dictionaries, sets, or custom objects.
# - Copies the entire object graph.
# - Nested mutable objects are copied independently.
#
# ================================================================================================================================

import copy

class Student:
    def __init__(self,name, age, department, projects):
        self.name = name
        self.age = age
        self.department = department
        self.projects= projects

    def clone(self):
        return copy.deepcopy(self)

    def __str__(self):
        return (f"Student(name)={self.name}, "
                f"age={self.age}, "
                f"department={self.department}, "
                f"projects={self.projects}) "

        )

if __name__=="__main__":
    student1 = Student("Sanjana", 25, "CS", ["DSA","LLD"])

    student2 = student1.clone()

    student2.name = "Priya"
    student2.age= 26
    student2.projects.append("System Design")

    print(student1)
    print(student2)

#---------------------------------------------------------------------------------------------------------------------------------
# Output:
# Student(name)=Sanjana, age=25, department=CS, projects=['DSA', 'LLD']) 
# Student(name)=Priya, age=26, department=CS, projects=['DSA', 'LLD', 'System Design']) 