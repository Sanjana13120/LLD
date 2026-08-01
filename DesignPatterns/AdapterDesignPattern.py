# ================================================================================================================================

# Adapter design pattern is a structural design pattern that allows two incompatible interfaces to work together. Instead of modiying exisiting code, we create an adapter class that converts one interface into another expected by the client.
#
# When to use:
# - When an existing class has an incompatible interface.
# - When modifying third-party or legacy code is not possible.
# - When we want to reuse existing classes without changing them.
#
# Example:
# Laptop expects a USB-C device.
# Mouse provides only a USB-A interface.
# The Adapter converts USB-A into USB-C, allowing both to work together.
#
# Components:
# 1. Target Interface - The interface expected by the client (USBC).
# 2. Adaptee - Existing class with an incompatible interface (USBAMouse).
# 3. Adapter - Converts the adaptee interface into the target interface.
# 4. Client - Uses the target interface (Laptop).
# ================================================================================================================================


from abc import ABC, abstractmethod

class USBC(ABC):
    @abstractmethod
    def connect(self):
        pass

class USBAdapter(USBC):
    def __init__(self,mouse):
        self.mouse=mouse

    def connect(self):
        self.mouse.connect_usba()

class USBAMouse:
    def connect_usba(self):
        print("USB-A Mouse connected")

class Laptop:
    def __init__(self,device: USBC):
            self.device=device

    def connect(self):
        self.device.connect()
        print("Laptop connected to USB-C device")

if __name__=="__main__":

    mouse = USBAMouse()
    adapter= USBAdapter(mouse)    # Adapter makes USB-A compatible with USB-C
    laptop=Laptop(adapter)
    laptop.connect()

    
# Output
# USB-A Mouse connected
# Laptop connected to USB-C device
    
