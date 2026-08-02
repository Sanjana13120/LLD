# ================================================================================================================================
# Bride is a structural design pattern that separates an abstraction from its implementation so that both can vary independently. It uses composition instead of inheritance to avoid a large number of subclasses.

#  When to use:
# - When an abstraction and its implementation should be developed separately.
# - When you want to avoid a large number of subclasses caused by combining multiple variations.
# - When both the abstraction and implementation may change independently.
# - When composition is preferred over inheritance.
#
# Without Bridge:    This leads to class explosion as TV brands and Remote types increase.
# SamsungBasicRemote
# SamsungAdvancedRemote
# SonyBasicRemote
# SonyAdvancedRemote
#
# With Bridge: Remote Control and TV --> Instead of creating separate classes like SamsungBasicRemote, SonyAdvancedRemote, etc.,  Bridge separates Remote (abstraction) from TV (implementation).
#
# Components:
# 1. Abstraction      --> Defines high-level control logic (Remote)
# 2. Refined Abstraction --> Extends abstraction features (BasicRemote, AdvancedRemote)
# 3. Implementation  --> Defines implementation interface (TV)
# 4. Concrete Implementation --> Actual implementations (Samsung, Sony)
# ================================================================================================================================

from abc import ABC, abstractmethod

class TV(ABC):
    @abstractmethod
    def turn_on(self):
        pass

    @abstractmethod
    def turn_off(self):
        pass

class Samsung(TV):
    def turn_on(self):
        print("Samsung tv is on")
    
    def turn_off(self):
        print("Samsung tv is off")

class Sony(TV):
    def turn_on(self):
        print("Sony tv is on")
    
    def turn_off(self):
        print("Sony tv is off")

class Remote(ABC):
    def __init__(self,tv: TV):
        self.tv=tv      #Bridge

    def power_on(self):
        self.tv.turn_on()

    def power_off(self):
        self.tv.turn_off()

class BasicRemote(Remote):
    pass

class AdvancedRemote(Remote):
    def voice_search(self):
        print("Voice search started")

    def youtube(self):
        print("Youtube started")

if __name__=="__main__":
    tv=Samsung()
    remote=BasicRemote(tv)
    remote.power_on()
    remote.power_off()

    tv=Sony()
    remote1=AdvancedRemote(tv)
    remote1.power_on()
    remote1.voice_search()
    remote1.youtube()
    remote1.power_off()

# Output
# Samsung tv is on
# Samsung tv is off
# Sony tv is on
# Voice search started
# Youtube started
# Sony tv is off