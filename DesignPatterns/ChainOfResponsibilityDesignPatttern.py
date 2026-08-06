# ================================================================================================================================
# The Chain of Responsibility Design Pattern is a behavioral design pattern that allows a request to pass through a chain of handlers. Each handler decides whether to process the request or forward it to the next handler in the chain.
#
# When to use:
# - When multiple objects can handle the same request.
# - When the handler is determined at runtime.
# - When you want to avoid tightly coupling the sender to a specific receiver.
# - When new handlers should be added without modifying existing code.
#
# Example:  A leave request is processed through different approval levels. Team Lead can approve up to 2 days, Manager up to 5 days, and Director approves any remaining requests.
#
# Components:
# 1. Handler          - Declares the interface for handling requests (Approver).
# 2. Concrete Handler - Processes the request or forwards it (TeamLead, Manager, Director).
# 3. Client           - Creates the chain and submits requests (main function).
#
# ================================================================================================================================

from abc import ABC, abstractmethod

# Handler: Defines the common interface for all approvers.
class Approver(ABC):
    def __init__(self):
        # Reference to the next approver in the chain.
        self.next_approver = None

    # Link the current approver to the next approver.
    def set_next(self,approver):
        self.next_approver=approver

    @abstractmethod
    def approve_leave(self,days):
        pass

# Concrete Handler: Approves leave requests up to 2 days.
class TeamLead(Approver):
    def approve_leave(self, days):
        if days<=2:
            print("Approved by Team Lead")

        # Forward the request to the next approver if it cannot be handled here.
        elif self.next_approver:
            self.next_approver.approve_leave(days) 

# Concrete Handler: Approves leave requests up to 5 days.
class Manager(Approver):
    def approve_leave(self, days):
        if days<=5:
            print("Approved by Manager")
        elif self.next_approver:
            self.next_approver.approve_leave(days)

# Final handler in the chain.  Handles all remaining leave requests
class Director(Approver):
    def approve_leave(self, days):
        print("Approved by Director")

# Client code
if __name__=="__main__":
    # Create the approvers
    teamlead=TeamLead()
    manager=Manager()
    director=Director()

    # Build the approval chain: TeamLead -> Manager -> Director
    teamlead.set_next(manager)
    manager.set_next(director)

    # Submit all leave requests to the first handler (TeamLead). TeamLead either handles the request or forwards it through  chain. The client does not directly invoke Manager or Director.
    teamlead.approve_leave(2)
    teamlead.approve_leave(5)
    teamlead.approve_leave(10)

# Output:
# Approved by Team Lead
# Approved by Manager
# Approved by Director