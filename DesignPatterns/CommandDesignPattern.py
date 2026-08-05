# ================================================================================================================================
# Command Design Pattern is a behavioural design pattern that encapsulates a request as an object. Instead of calling methods directly on an object, the request is wrapped inside a Command object, allowing it to be executed, queued, logged, or even undone later.
#
# When to use:
# - When you want to decouple the object that invokes an operation from the object that performs it.
# - When different requests need to be parameterized as objects.
# - When implementing menu items, buttons, remote controls, task queues, or schedulers.
# - When supporting undo/redo functionality.
# - When commands need to be logged or executed at a later time.
#
# Example:
# A TV remote control doesn't know how to turn on or off a TV. It simply executes the assigned command. The command knows which TV to control and what action to perform.
#
# Components:
# 1. Receiver - The object that knows how to perform the actual work (TV).
# 2. Command - Interface declaring the execute() method.
# 3. Concrete Command - Implements execute() by invoking operations on the Receiver (TurnOnCommand, TurnOffCommand).
# 4. Invoker - Stores a command and triggers its execution (Remote).
# 5. Client - Creates the Receiver, Commands, assigns them to the Invoker, and initiates execution (main function).
#
# ================================================================================================================================

from abc import ABC, abstractmethod

# Receiver: Defines the operations that concrete TVs must implement.
class TV(ABC):    
    @abstractmethod
    def turn_on(self):
        pass
    @abstractmethod
    def turn_off(self):
        pass

# Concrete Receiver: Samsung TV implementation
class SamsungTV(TV):
    def turn_off(self):
        print("Samsung tv turned off")

    def turn_on(self):
            print("Samsung tv turned on")

# Command interface: Every command must implement execute().
class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

# Concrete Command: Turns the TV ON.
class TurnOnCommand(Command):
    def __init__(self,tv:TV):
        self.tv=tv

    def execute(self):
        self.tv.turn_on()

# Concrete Command: Turns the TV OFF.
class TurnOffCommand(Command):
    def __init__(self,tv:TV):
        self.tv=tv

    def execute(self):
        self.tv.turn_off()

# Invoker: Executes the assigned command without knowing its implementation.
class Remote:
    def __init__(self,command:Command):
        self.command=command

    def press_button(self):
        self.command.execute()

# Client code
if __name__=="__main__":
    tv=SamsungTV()                     # Create the receiver

    # Create command objects
    on_command=TurnOnCommand(tv)
    off_command=TurnOffCommand(tv)

    # Assign ON command to the remote and execute
    remote=Remote(on_command)
    remote.press_button()

    # Assign OFF command to the remote and execute
    remote=Remote(off_command)
    remote.press_button()

# Output:
# Samsung tv turned on
# Samsung tv turned off