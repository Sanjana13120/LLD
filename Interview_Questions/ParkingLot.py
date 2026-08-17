# Objective: Design a Parking Lot

# Step 1: Functional Requirements
# 1. entry and exit gate 
# 2. Vehicle type
# 3. Availabillty of parking slot
# 4. record timestamp
# 5. calculate the parking fee based on duration/type
# 6. Make payement
# 7. generate parking ticket

# Step2: Non-Functional Requirements
# 1. Thread safe - Multiple vehicles can enter/exit simultaneously

# Step 3: Identify the core entities
# ParkingLot
#     - ParkingFloor
#         -ParkingSpot
#           -BikeSpot
#           -CarSpot
#           -EVSpot
#     - EntryGate
#     -ExitGate
#     -DisplayBoard

# Vehicle
#     Car
#     Bike

# ParkingSpot status - enum
# AVAILABLE
# OCCUPIED

# Ticket
# Payment

# We will be using strategy design pattern for parkingspotAllocation
# for display board we will be using observer design pattern

# and for thread safety -- race condition/synchronization

# Step 4: Identify Relationship

# Vehicle ─── Ticket ─── ParkingSpot --> this is association (vehicle/spot don't own each other's lifecycle)
# ParkingLot ◆── ParkingFloor   --> aggregation
# ParkingFloor ◆── ParkingSpot  --> aggregation (the lot owns its floors and floors own their spots.)

# Step 5: Core Operations:

# ParkingLot
#     ParkingSpot
#     park_vehicle()
#     entry_Vehicle()
#     exit_vehicle()
#     display()

# ParkingSpot
#     spot_id, spot_type, status
#     canFcan_fit(Vehicle)
#     occupy()
#     release()
#    
# Ticket
#     ticket_id
#     Vehicle
#        VehicleType
#        number
#     spot
#     entryTime
#     exitTime

# Step 6: Coding

from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
from math import ceil
import threading


class Vehicle:
    def __init__(self,vehicle_type, vehicle_number):
        self.vehicle_type=vehicle_type
        self.vehicle_number=vehicle_number

class VehicleType(Enum):
    BIKE="Bike"
    CAR="Car"

class TicketStatus(Enum):
    ACTIVE="Active"
    CLOSED="Closed"
 
class ParkingSpotStatus(Enum):
    OCCUPIED="Occupied"
    AVAILABLE="Available"

class PaymentStatus(Enum):
    SUCCESSFUL="Successful"
    FAILED="Failed"
    
class ParkingSpot:
    def __init__(self,spot_id, floor_number, spot_type):
        self.spot_id=spot_id
        self.spotStatus=ParkingSpotStatus.AVAILABLE 
        self.spot_type=spot_type
        self.floor_number=floor_number
        self.vehicle=None
        self.lock=threading.Lock()

    def can_fit(self, vehicle: Vehicle):
        return vehicle.vehicle_type==self.spot_type

    def is_available(self):
        return self.spotStatus==ParkingSpotStatus.AVAILABLE

    def park(self,vehicle):
        with self.lock:
            if self.is_available():
                self.vehicle=vehicle
                self.spotStatus=ParkingSpotStatus.OCCUPIED
            
                return True
            return False

    def release(self):
        with self.lock:
            if not self.is_available():
                self.vehicle=None
                self.spotStatus=ParkingSpotStatus.AVAILABLE
                return True
            return False

class ParkingFloor:
    def __init__(self, floor_number):
        self.spots=[]
        self.floor_number=floor_number
        self.observers=[]
        self.available_count={} 

    def add_spot(self,spot: ParkingSpot):
        self.spots.append(spot)
        self.available_count[spot.spot_type]= self.available_count.get(spot.spot_type,0)+1

    def add_observer(self,observer):
        self.observers.append(observer)

    def notify_observers(self):
        for observer in self.observers:
            observer.update()

    def park_vehicle(self,spot,vehicle):
        if spot.park(vehicle):
            self.available_count[spot.spot_type]-=1
            self.notify_observers()
            return True
        return False

    def release_vehicle(self,spot):
        if spot.release():
            self.available_count[spot.spot_type]+=1
            self.notify_observers()
            return True
        return False
    
class Observer(ABC):
    @abstractmethod
    def update(self):
        pass

class DisplayBoard(Observer):
    def __init__(self,floor):
        self.floor=floor

    def update(self):
        print(f"Floor:{self.floor.floor_number}")

        available = {spot_type.value: count for spot_type, count in self.floor.available_count.items()}

        print(f"Available spots: {available}")

class ParkingSpotAllocationStrategy(ABC):
    @abstractmethod
    def allocate_spot(self, floors, vehicle):
        pass

class FirstAvailableParkingSpot(ParkingSpotAllocationStrategy):
    def allocate_spot(self,floors,vehicle: Vehicle):
        for floor in floors:
            for spot in floor.spots:
                if spot.is_available() and spot.can_fit(vehicle):
                    return floor,spot
        return None

class Ticket:
    def __init__(self,ticket_id, vehicle: Vehicle, floor, parking_spot: ParkingSpot):
        self.ticket_id=ticket_id
        self.entry_time=datetime.now()
        self.vehicle=vehicle
        self.floor=floor
        self.parking_spot=parking_spot
        self.exit_time=None
        self.amount=0.0
        self.status=TicketStatus.ACTIVE
        self.payment_method = None

    def generate_entry_ticket(self):
        print("\n========== ENTRY TICKET ==========")
        print(f"Ticket ID    : {self.ticket_id}")
        print(f"Vehicle      : {self.vehicle.vehicle_number}")
        print(f"Vehicle Type : {self.vehicle.vehicle_type.value}")
        print(f"Floor        : {self.floor.floor_number}")
        print(f"Spot         : {self.parking_spot.spot_id}")
        print(f"Entry Time   : {self.entry_time}")
        print(f"Status       : {self.status.value}")
        print("====================================\n")

    def generate_exit_ticket(self):
        print("\n========== EXIT TICKET ==========")
        print(f"Ticket ID    : {self.ticket_id}")
        print(f"Vehicle      : {self.vehicle.vehicle_number}")
        print(f"Vehicle Type : {self.vehicle.vehicle_type.value}")
        print(f"Floor        : {self.floor.floor_number}")
        print(f"Spot         : {self.parking_spot.spot_id}")
        print(f"Entry Time   : {self.entry_time}")
        print(f"Exit Time    : {self.exit_time}")
        print(f"Amount       : {self.amount}")
        print(f"Payment      : {self.payment_method}")
        print(f"Status       : {self.status.value}")
        print("=================================\n")

class ParkingFeeStrategy(ABC):
    @abstractmethod
    def calculate(self,ticket):
        pass

class SimpleParkingFeeStrategy(ParkingFeeStrategy):
    def calculate(self, ticket):
        duration=ticket.exit_time - ticket.entry_time
        hours=ceil(duration.total_seconds()/3600)

        if ticket.vehicle.vehicle_type==VehicleType.CAR:
            return hours*50
        if ticket.vehicle.vehicle_type==VehicleType.BIKE:
            return hours*20

        return 0

class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self,amount):
        pass

class UPIPaymentStrategy(PaymentStrategy):
    def pay(self,amount):
        return PaymentStatus.SUCCESSFUL

class ParkingLot:
    def __init__(self, spot_allocation_strategy: ParkingSpotAllocationStrategy, fee_strategy: ParkingFeeStrategy, payment_strategy: PaymentStrategy):
        self.floors=[]
        self.tickets={}
        self.next_ticket_id=1

        self.entry_lock = threading.Lock()
        self.exit_lock = threading.Lock()
        
        self.spot_allocation_strategy=spot_allocation_strategy
        self.fee_strategy=fee_strategy
        self.payment_strategy= payment_strategy
        

    def add_floor(self,floor: ParkingFloor):
        self.floors.append(floor)

    def entry_vehicle(self,vehicle: Vehicle):
        with self.entry_lock:
            allocation =self.spot_allocation_strategy.allocate_spot(self.floors, vehicle)
            
            if allocation is None:
                print("No spots are available\n")
                return None
            
            floor,spot=allocation
             
            if not floor.park_vehicle(spot,vehicle):
                return None
             
            
            ticket_id=self.next_ticket_id
            self.next_ticket_id+=1
             
            ticket=Ticket(ticket_id, vehicle,floor, spot)
             
            self.tickets[ticket_id]=ticket
            ticket.generate_entry_ticket()
             
            return ticket                            

    def exit_vehicle(self, vehicle: Vehicle):
        with self.exit_lock:
            for ticket_id, ticket in self.tickets.items():
                if ticket.vehicle == vehicle and ticket.status == TicketStatus.ACTIVE:
                    ticket.exit_time=datetime.now()

                    ticket.amount=self.fee_strategy.calculate(ticket)

                    payment_status=self.payment_strategy.pay(ticket.amount)

                    if payment_status==PaymentStatus.SUCCESSFUL: 
                        ticket.payment_method="UPI"       
                        released= ticket.floor.release_vehicle(ticket.parking_spot)
                        if released:
                            ticket.status=TicketStatus.CLOSED
                            ticket.generate_exit_ticket()
                            return ticket
                    
                    return None

            return None


if __name__=="__main__":
    # Create strategies
    spot_allocation_strategy= FirstAvailableParkingSpot()
    fee_strategy=SimpleParkingFeeStrategy()
    payment_strategy=UPIPaymentStrategy()

    # Create parking lot
    lot = ParkingLot(spot_allocation_strategy,fee_strategy,payment_strategy)

    # Create floor
    floor1=ParkingFloor(1)
    lot.add_floor(floor1)

    # Create parking spots
    car_spot=ParkingSpot(spot_id=1, floor_number=1, spot_type=VehicleType.CAR)
    bike_spot=ParkingSpot(spot_id=2, floor_number=1, spot_type=VehicleType.BIKE)

    floor1.add_spot(car_spot)
    floor1.add_spot(bike_spot)

    # Register display board as observer
    display_board=DisplayBoard(floor1)
    floor1.add_observer(display_board)

    # ---------- CAR 1 ENTRY ----------
    car1=Vehicle(VehicleType.CAR, "KA01AB1234")
    car1_ticket=lot.entry_vehicle(car1)

    # ---------- CAR 2 ENTRY ---------- 
    # No CAR spot available
    car2=Vehicle(VehicleType.CAR, "KA01AB4567")
    car2_ticket=lot.entry_vehicle(car2)

    # ---------- CAR 1 EXIT ----------

    closed_ticket=lot.exit_vehicle(car1)

    # ---------- CAR 2 ENTRY AGAIN ---------- 
    # CAR spot is now available
    car2_ticket=lot.entry_vehicle(car2)

    # ---------- BIKE ENTRY ----------
    bike=Vehicle(VehicleType.BIKE, "KA01AB9876")
    bike_ticket=lot.entry_vehicle(bike)

    # ---------- BIKE EXIT ----------
    bike_closed_ticket=lot.exit_vehicle(bike)

# ============================================================================================================================
#
# Output
# Floor:1
# Available spots: {'Car': 0, 'Bike': 1}

# ========== ENTRY TICKET ==========
# Ticket ID    : 1
# Vehicle      : KA01AB1234
# Vehicle Type : Car
# Floor        : 1
# Spot         : 1
# Entry Time   : 2026-08-17 15:05:12.388936
# Status       : Active
# ====================================

# No spots are available

# Floor:1
# Available spots: {'Car': 1, 'Bike': 1}

# ========== EXIT TICKET ==========
# Ticket ID    : 1
# Vehicle      : KA01AB1234
# Vehicle Type : Car
# Floor        : 1
# Spot         : 1
# Entry Time   : 2026-08-17 15:05:12.388936
# Exit Time    : 2026-08-17 15:05:12.389294
# Amount       : 50
# Payment      : UPI
# Status       : Closed
# =================================

# Floor:1
# Available spots: {'Car': 0, 'Bike': 1}

# ========== ENTRY TICKET ==========
# Ticket ID    : 2
# Vehicle      : KA01AB4567
# Vehicle Type : Car
# Floor        : 1
# Spot         : 1
# Entry Time   : 2026-08-17 15:05:12.389809
# Status       : Active
# ====================================

# Floor:1
# Available spots: {'Car': 0, 'Bike': 0}

# ========== ENTRY TICKET ==========
# Ticket ID    : 3
# Vehicle      : KA01AB9876
# Vehicle Type : Bike
# Floor        : 1
# Spot         : 2
# Entry Time   : 2026-08-17 15:05:12.390207
# Status       : Active
# ====================================

# Floor:1
# Available spots: {'Car': 0, 'Bike': 1}

# ========== EXIT TICKET ==========
# Ticket ID    : 3
# Vehicle      : KA01AB9876
# Vehicle Type : Bike
# Floor        : 1
# Spot         : 2
# Entry Time   : 2026-08-17 15:05:12.390207
# Exit Time    : 2026-08-17 15:05:12.390440
# Amount       : 20
# Payment      : UPI
# Status       : Closed
# =================================
   
# ============================================================================================================================


