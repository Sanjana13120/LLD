# ================================================================================================================================
# Composite is a structural design pattern that allows us to treat individual objcts (leaf) and group of objects (composite) uniformly through a common interface. 
#
# When to use:
# - When objects naturally form a tree-like hierarchy.
# - When clients should treat single objects and groups of objects uniformly.
# - When recursive structures (file systems, organization charts, menus, etc.) need to be represented.
# - When adding or removing child objects dynamically.
#
# Example: File System --> Instead of writing separate code for files and folders, both implement the same interface so that the client can work with them in the same way.
#
# Without Composite: Client needs separate logic for Files and Folders.
# Client has to check:
# 1. If object is File -> display file.
# 2. If object is Folder -> display folder and iterate through its children.
#
# With Composite: Client simply calls display() on any FileSystemComponent.
# The composite (Folder) automatically displays all its children recursively.
#
# Components:
# 1. Component: Common interface for both leaf and composite objects.
#    Example: FileSystemComponent
#
# 2. Leaf: Represents individual objects with no children.
#    Example: File
#
# 3. Composite: Represents objects that can contain other components.
#    Example: Folder
#
# 4. Client: Works with Component objects without worrying whether they are individual objects or groups.
#    Example: root.display()
#
# ================================================================================================================================

from abc import ABC, abstractmethod

class FileSystemComponent(ABC):
    @abstractmethod
    def display(self):
        pass

class File(FileSystemComponent):
    def __init__(self,filename,filesize):
        self.filename=filename
        self.filesize=filesize

    def display(self):
        print(f"File: {self.filename} ({self.filesize})")

class Folder(FileSystemComponent):
    def __init__(self,name):
        self.name=name
        self.children=[]

    def add(self,component: FileSystemComponent):
        self.children.append(component)

    def remove(self,component: FileSystemComponent):
        self.children.remove(component)

    def display(self):
         print(f"Folder: {self.name}")

         for child in self.children:
            child.display()

if __name__=="__main__":
    root=Folder("root")
    resume= File("Resume.pdf","2GB")
    notes=File("Notes.txt","1GB")
    projects=Folder("Projects")
    app=File("app.py","3GB")
    test=File("test.py","2GB")

    root.add(resume)
    root.add(notes)
    root.add(projects)

    projects.add(app)
    projects.add(test)

    root.display()

# Output:
# Folder: root
#   File: Resume.pdf (2GB)
#   File: Notes.txt (1GB)
#   Folder: Projects
#       File: app.py (3GB)
#       File: test.py (2GB)