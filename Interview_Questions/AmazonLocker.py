"""
# Objective: Design an Amazon Locker system where delivery agents can place packages into available lockers, and customers can retrieve their packages using a pickup code.

1. Funtional Requirements:
1) Delivery agent should be able to place package in locker based on the size.
2) System should find appropriate locker
3) Customer uses pickup code to retrieve the package
4) system generates pickup code
5) Pickup code expires after 48 hours. Expired pickup codes cannot be used for pickup.
6) locker becomes available after package retrival
7) An expired pickup code does NOT automatically free the locker. The package remains in the locker until a separate operational process handles it (e.g. return to sender).

2. Non - Funtional Requirements:
1) thread safety/concurrency - Two delivery agents shouldn't be able to assign the same locker concurrently.
2) Extensibiltiy - to new allocation and pickup code
3) Performance/ Reliability

3. Identify core entities:
  
Package
   - package_id, address, package_size, customer, locker_id
   - enums - small/medium/large

PickupCode
    - code
    - package_id
    - expires_at
    - status

    + isValid(code)

Customer
    - customer_id
    - customer_name   

Locker  → manages its own package/state
    - locker_id, package, locker_size, locker_status (AVAILABLE/OCCUPIED)

    + can_fit(package)
    + store_package(package)
    + pickup_package()

LockerSystem   → manages collection of lockers
   - lockers = {}

   + add_locker(locker)
   + get_locker(locer_id)
   + get_available_lockers()
   

LockerSystemManager - → coordinates use cases (orcdestrator)
   - LockerSystem
   - LockerAllocationStrategy
   - pickupcodestrategy
   - locker

   + place_package(package)
   + pickup_package(code)

   
LockerAllocationStrategy  → decides which locker to allocate
    + find_locker(package, lockers) --> BestFitStrategy/ NearestAvailable and so on...

PickupCodeGeneratorStrategy - OTPPickupCodeStrategy    → generates pickup code
    + generate_code()


4. Identify relationship

Delivery agent -> place package -> lockers and customer -> pickup code -> retrieve package

LockerSystem --has a--> Locker (1 - MANY)
Locker --has a --> Package (1-0/1)

DeliveryAgent --USES--> LockerSystem
Customer --USES--> LockerSystem

Customer --has--> Package (1-MANY)
Package --has--> PickupCode (1-1)

LockerSystemManager --USES--> LockerSystem
LockerSystemManager --USES--> LockerAllocationStrategy
LockerSystemManager --USES--> PickupCodeGeneratorStrategy

5. Coding

"""
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime, timedelta
import random,threading

class Size(Enum):
    SMALL = 1
    MEDIUM = 2
    LARGE = 3    

class LockerStatus(Enum):
    AVAILABLE = "Available"
    OCCUPIED = "Occupied"

class PickupCodeStatus(Enum):
    ACTIVE = "Active"
    EXPIRED = "Expired"

class Package:
    def __init__(self, package_id, package_size : Size, address, locker_id = None):
        self.package_id = package_id
        self.address = address
        self.package_size = package_size
        self.locker_id = locker_id
        self.pickup_code = None

class PickupCode:
    def __init__(self, pickup_code, package_id, expires_at):
        self.pickup_code = pickup_code
        self.package_id = package_id
        self.expires_at = expires_at
        self.code_status = PickupCodeStatus.ACTIVE

    def isValid(self):
        if self.code_status == PickupCodeStatus.EXPIRED:
            return False
        
        if datetime.now() > self.expires_at:
            self.code_status = PickupCodeStatus.EXPIRED
            return False

        return True

class Locker:
    def __init__(self,locker_id, locker_size):
        self.locker_id = locker_id
        self.package = None
        self.locker_size = locker_size
        self.locker_status = LockerStatus.AVAILABLE
        self.pickup_code = None

    def can_fit(self,package): 
        return self.locker_status == LockerStatus.AVAILABLE and self.locker_size.value >= package.package_size.value

    def store_package(self, package, pickup_code):
        if not self.can_fit(package):
            return False
        
        self.package = package
        self.locker_status = LockerStatus.OCCUPIED
        self.pickup_code = pickup_code

        package.locker_id = self.locker_id
        package.pickup_code = pickup_code
        return True

    def release_package(self, pickup_code):
        if self.package is None or pickup_code!= self.pickup_code.pickup_code:
            return None
        
        if not self.pickup_code.isValid():
            return None
        
        package = self.package
        self.package = None
        self.locker_status = LockerStatus.AVAILABLE
        self.pickup_code = None

        package.locker_id = None
        package.pickup_code = None

        return package

class DuplicatePickupCodeError(RuntimeError):
    pass
        
class LockerSystem:
    def __init__(self):
        self.lockers = {}
        self.pickup_code_to_locker = {}

    def add_locker(self,locker:Locker):
        self.lockers[locker.locker_id] = locker

    def get_locker(self,locker_id):
        return self.lockers.get(locker_id)

    def get_available_lockers(self):
        return [locker for locker in self.lockers.values() if locker.locker_status == LockerStatus.AVAILABLE]

    def register_pickup_code(self, code, locker):
        if code in self.pickup_code_to_locker:
            raise DuplicatePickupCodeError("Duplicate pickup code")

        self.pickup_code_to_locker[code] = locker
        
    def get_locker_by_pickup_code(self,code):
        return self.pickup_code_to_locker.get(code)

    def remove_pickup_code(self,code):
        self.pickup_code_to_locker.pop(code, None)

class LockerAllocationStrategy(ABC):
    @abstractmethod
    def find_locker(self,package, lockers):
        pass

class BestFitAllocationStrategy(LockerAllocationStrategy):
    def find_locker(self, package, lockers):
        best = [locker for locker in lockers if locker.can_fit(package)]
        if not best:
            return None

        return min(best, key=lambda locker: locker.locker_size.value)

class PickupCodeGeneratorStrategy(ABC):
    @abstractmethod
    def generate_code(self):
        pass

class OTPPickupCodeStrategy(PickupCodeGeneratorStrategy):
    def generate_code(self):
        return f"{random.randint(0,999999):06d}"

class NoLockerAvailableError(RuntimeError):
    pass

class InvalidPickupCodeError(RuntimeError):
    pass

class LockerSystemManager:
    def __init__(self, locker_system: LockerSystem, locker_allocation_strategy: LockerAllocationStrategy, pickup_code_strategy: PickupCodeGeneratorStrategy):
        self.locker_system = locker_system
        self.locker_allocation_strategy = locker_allocation_strategy
        self.pickup_code_strategy = pickup_code_strategy

        # The manager coordinates the complete operation: find locker → store package → register pickup code. Therefore, the critical section should cover the whole allocation flow.

        self.lock = threading.Lock()

    def place_package(self,package):
        with self.lock:
            #get the available locker from LockerSystem
            available_lockers = self.locker_system.get_available_lockers()

            #find the best fit locker from list of lockers
            locker = self.locker_allocation_strategy.find_locker(package,available_lockers)
            if locker is None:
                raise NoLockerAvailableError(f"No locker available for package {package.package_id} | size: {package.package_size} ")

            #otherwise Generate a unique pickup code
            while True:
                code  = self.pickup_code_strategy.generate_code()
                if self.locker_system.get_locker_by_pickup_code(code) is None:
                    break

            # Create pickup code with 48-hour expiry
            expires_at = datetime.now() + timedelta(hours=48)
            pickup_code = PickupCode(code, package.package_id, expires_at)

            # Store package and register pickup code
            locker.store_package(package, pickup_code)
            self.locker_system.register_pickup_code(code,locker)

            return locker.locker_id , pickup_code

    def pickup_package(self,pickup_code):
        with self.lock:
            # find the locker 
            locker = self.locker_system.get_locker_by_pickup_code(pickup_code)
            if locker is None:
                raise InvalidPickupCodeError("Invalid pickup code")

            # pickup the package
            package = locker.release_package(pickup_code)
            if package is None:
                raise InvalidPickupCodeError("Invalid pickup code")
            
            # remove code mapping
            self.locker_system.remove_pickup_code(pickup_code)

            return package
        
def main():
    locker_system = LockerSystem()
    for i in range(1,3):
        locker_system.add_locker(Locker(f"S{i}",Size.SMALL))
    for i in range(1,3):
        locker_system.add_locker(Locker(f"M{i}",Size.MEDIUM))

    locker_system.add_locker(Locker(f"L1",Size.LARGE))

    locker_allocation_strategy = BestFitAllocationStrategy()
    pickup_code_strategy = OTPPickupCodeStrategy()

    manager = LockerSystemManager(locker_system, locker_allocation_strategy, pickup_code_strategy )

    small_pkg = Package("P1", Size.SMALL, "221B Baker Street")
    medium_pkg = Package("P2", Size.MEDIUM, "42 Bay street")
    large_pkg = Package("P3", Size.LARGE, "97 Chelsea street")

    print("Placing packages:")
    for pkg in (small_pkg, medium_pkg, large_pkg):
        locker, pickup_code = manager.place_package(pkg)
        print(f"{pkg.package_id} placed in locker {locker}, pickup code {pickup_code.pickup_code} expires at {pickup_code.expires_at}")
    try:
        print("\nAttempting pickup with a wrong code:")
        manager.pickup_package("000000")
    except InvalidPickupCodeError  as e:
        print(f"Pickup failed: {e}")

    print("\nPicking up with correct code")
    pickup = manager.pickup_package(small_pkg.pickup_code.pickup_code)   
    print(f"Package {pickup.package_id} picked") 

    print(f"\nLocker S1 Status: {locker_system.get_locker("S1").locker_status.value}")
    print(f"Locker M1 Status: {locker_system.get_locker("M1").locker_status.value }")
    print(f"Locker L1 Status: {locker_system.get_locker("L1").locker_status.value }")

    print("\nPlacing another small package:")
    small_pkg_2 = Package("P4", Size.SMALL, "10 Downing Street")
    locker, pickup_code = manager.place_package(small_pkg_2) 
    print(f"{small_pkg_2.package_id} placed in locker {locker}, pickup code {pickup_code.pickup_code} expires at {pickup_code.expires_at}")
    print(f"Locker {locker} Status: {locker_system.get_locker(locker).locker_status.value}")

    print("\nPlacing another large package:")
    large_pkg_2 = Package("P5", Size.LARGE, "42 ABC Street")
    try:
        locker, pickup_code = manager.place_package(large_pkg_2)
        print(f"{large_pkg_2.package_id} placed in locker {locker}, pickup code {pickup_code.pickup_code} expires at {pickup_code.expires_at}")
        print(f"Locker {locker} Status: {locker_system.get_locker(locker).locker_status.value}")
    except NoLockerAvailableError as e:
        print(f"Placement failed {e}")


if __name__ == "__main__":
    main()