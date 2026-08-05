# ================================================================================================================================
# State Design Pattern is a behavioural design pattern that allows an object to alter its behavior when its internal state changes. The object appears to change its class by delegating state-specific behavior to separate State objects.
#
# When to use:
# - When an object's behavior depends on its current state.
# - When there are many conditional statements (if-else or switch-case) based on state.
# - When state transitions are well-defined.
# - When you want to add new states without modifying existing ones.
#
# Example: A music player behaves differently depending on whether it is Stopped, Playing, or Paused. Pressing the Play button starts or resumes music, while pressing Pause or Stop behaves differently in each state.
#
# Components:
# 1. State - Interface declaring operations for each state.
# 2. Concrete State - Implements state-specific behavior and transitions (StoppedState, PlayingState, PausedState).
# 3. Context - Maintains the current state and delegates requests to it (MusicPlayer).
# 4. Client - Creates the Context and invokes operations (main function).
#
# ================================================================================================================================


from abc import ABC, abstractmethod

# State interface: Defines actions that every concrete state must implement.
class State(ABC):
    @abstractmethod
    def play(self,player):
        pass

    @abstractmethod
    def stop(self,player):
        pass

    @abstractmethod
    def pause(self,player):
        pass

# Context: Maintains the current state and delegates requests to it.
class MusicPlayer:
    # Music player starts in the Stopped state.
    def __init__(self):
        self.state=StoppedState() 

    # Delegate play request to the current state.
    def play(self): 
        self.state.play(self)

     # Delegate pause request to the current state.
    def pause(self):
        self.state.pause(self)

    # Delegate stop request to the current state.
    def stop(self):
        self.state.stop(self)

#Concrete State: Represents the music player when stopped.
class StoppedState(State):
    # Start playing music and transition to PlayingState.
    def play(self,player):
        print("Playing music")
        player.state=PlayingState()

    # Already stopped; no state change.
    def stop(self,player):
        print("Already music stopped")

    # Cannot pause when music is stopped.
    def pause(self, player):
        print("Cannot pause. Music is stopped.")

# Concrete State: Represents the music player while playing.
class PlayingState(State):
    # Already playing; no state change.
    def play(self, player):
        print("Already playing.")

    # Stop the music and transition to StoppedState.
    def stop(self,player):
        print("Music is stopped.")
        player.state=StoppedState()

    # Pause the music and transition to PausedState.    
    def pause(self, player):
        print("Music is paused.")
        player.state=PausedState()

# Concrete State: Represents the music player while paused.
class PausedState(State):
    # Resume playing and transition to PlayingState.
    def play(self, player):
        print("Resuming Music")
        player.state=PlayingState()

    # Stop the music and transition to StoppedState.
    def stop(self,player):
        print("Music stopped")
        player.state=StoppedState()

    # Already paused; no state change.    
    def pause(self, player):
        print("Music is already paused.")

# Client code
if __name__=="__main__":
    music = MusicPlayer() # Create the Context object.

    music.play()    # State transitions: Stopped -> Playing

    music.play()    # Playing -> Playing (no state change)

    music.pause()   # Playing -> Paused

    music.play()    # Paused -> Playing

    music.stop()     # Playing -> Stopped

    music.stop()     # Stopped -> Stopped (no state change)

# Output
# Playing music
# Already playing.
# Music is paused.
# Resuming Music
# Music is stopped.
# Already music stopped