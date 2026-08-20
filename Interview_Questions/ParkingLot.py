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
# ParkingLot ◆── ParkingFloor   --> Composition
# ParkingFloor ◆── ParkingSpot  --> Composition (the lot owns its floors and floors own their spots.)

# Step 5: Core Operations:

# ParkingLot
#     ParkingSpot
#     park_vehicle()
#     entry_Vehicle()
#     exit_vehicle()
#     display()

# ParkingSpot
#     spot_id, spot_type, status
#     can_fit(Vehicle)
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

class VehicleType(Enum):
    CAR="Car"
    BIKE="Bike"
    TRUCK="Truck"

class SpotType(Enum):
    BIKE="Bike"
    COMPACT="Compact"
    LARGE="Large"

class SpotStatus(Enum):
    AVAILABLE="Available"
    OCCUPIED="Occupied"

class TicketStatus(Enum):
    ACTIVE="Active"
    CLOSED="Closed"

class PaymentStatus(Enum):
    SUCCESSFUL="Successful"
    FAILED="Failed"

SPOT_FITS={SpotType.BIKE: {VehicleType.BIKE}, 
           SpotType.COMPACT: {VehicleType.CAR},
           SpotType.LARGE: {VehicleType.TRUCK, VehicleType.CAR} }

class Vehicle:
    def __init__(self,vehicle_type, vehicle_number):
        self.vehicle_type=vehicle_type
        self.vehicle_number=vehicle_number

class ParkingSpot:
    def __init__(self,spot_id, spot_type):
        self.spot_id=spot_id
        self.spot_type=spot_type
        self.spot_status=SpotStatus.AVAILABLE
        self.vehicle=None

    def can_fit(self,vehicle: Vehicle):
        return vehicle.vehicle_type in SPOT_FITS[self.spot_type]

    def is_available(self):
        return self.spot_status==SpotStatus.AVAILABLE

    def park(self,vehicle):
        if not self.is_available():
            return False
        if not self.can_fit(vehicle):
            return False
        
        self.vehicle=vehicle
        self.spot_status=SpotStatus.OCCUPIED
        return True

    def unpark(self,vehicle):
        if not self.is_available() and self.vehicle==vehicle:
            self.vehicle=None
            self.spot_status=SpotStatus.AVAILABLE
            return True
        
        return False

class ParkingFloor:
    def __init__(self,floor_number):
        self.floor_number=floor_number
        self.spots=[]
        self.observers=[]
        self.available_count={}

    def add_spots(self, spot:ParkingSpot):
        self.spots.append(spot)
        self.available_count[spot.spot_type]=self.available_count.get(spot.spot_type,0)+1

    def add_observer(self,observer):
        self.observers.append(observer)

    def notify_observers(self):
        for observer in self.observers:
            observer.update(self)

    def occupy_spot(self,spot):
        self.available_count[spot.spot_type]-=1
        self.notify_observers()
        

    def release_spot(self,spot):
        self.available_count[spot.spot_type]+=1
        self.notify_observers()
    
class Observer(ABC):
    @abstractmethod
    def update(self,floor):
        pass

class DisplayBoard(Observer):

    def update(self,floor):
        print(f"Floor number:{floor.floor_number}")

        available = {spot_type.value: count for spot_type, count in floor.available_count.items()}

        print(f"Available spots: {available}")

class ParkingSpotAllocationStrategy(ABC):
    @abstractmethod
    def allocate_spot(self,vehicle:Vehicle,floors):
        pass

class FindAvailableSpotStrategy(ParkingSpotAllocationStrategy):
    def allocate_spot(self, vehicle:Vehicle,floors):
        for floor in floors:
            for spot in floor.spots:
                if spot.is_available() and spot.can_fit(vehicle):
                    return floor,spot
        return None      

class Ticket:
    def __init__(self,ticket_id, vehicle: Vehicle,floor, spot: ParkingSpot):
        self.ticket_id=ticket_id
        self.vehicle=vehicle
        self.spot=spot
        self.floor=floor
        self.entry_time=datetime.now()
        self.exit_time=None
        self.amount=0.0
        self.ticket_status=TicketStatus.ACTIVE

    def print_entry_ticket(self):
        print("\n========== ENTRY TICKET ==========")
        print(f"Ticket ID    : {self.ticket_id}")
        print(f"Vehicle      : {self.vehicle.vehicle_number}")
        print(f"Vehicle Type : {self.vehicle.vehicle_type.value}")
        print(f"Floor        : {self.floor.floor_number}")
        print(f"Spot         : {self.spot.spot_id}")
        print(f"Entry Time   : {self.entry_time}")
        print(f"Status       : {self.ticket_status.value}")
        print("====================================\n")

    def print_exit_ticket(self, payment_method):
        print("\n========== EXIT TICKET ==========")
        print(f"Ticket ID    : {self.ticket_id}")
        print(f"Vehicle      : {self.vehicle.vehicle_number}")
        print(f"Vehicle Type : {self.vehicle.vehicle_type.value}")
        print(f"Floor        : {self.floor.floor_number}")
        print(f"Spot         : {self.spot.spot_id}")
        print(f"Entry Time   : {self.entry_time}")
        print(f"Exit Time    : {self.exit_time}")
        print(f"Amount       : {self.amount}")
        print(f"Payment      : {payment_method}")
        print(f"Status       : {self.ticket_status.value}")
        print("=================================\n")

class ParkingFeeStrategy(ABC):
    @abstractmethod
    def calculate_fee(self,ticket):
        pass

class SimpleFeeStrategy(ParkingFeeStrategy):
    Hourly_rates={VehicleType.BIKE: 20, VehicleType.CAR: 50, VehicleType.TRUCK: 100}

    def calculate_fee(self, ticket):
        duration=ticket.exit_time - ticket.entry_time
        hours=ceil(duration.total_seconds()/3600)

        rate=self.Hourly_rates[ticket.vehicle.vehicle_type]

        return hours*rate

class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self,amount):
        pass
    @abstractmethod
    def get_payment_method(self):
        pass

class UPIPayment(PaymentStrategy):
    def pay(self, amount):
        print(f"Paid {amount} paid by UPI")
        return PaymentStatus.SUCCESSFUL
        
    def get_payment_method(self):
        return "UPI"

class CardPayment(PaymentStrategy):
    def pay(self, amount):
        print(f"Paid {amount} paid by Card")
        return PaymentStatus.SUCCESSFUL


    def get_payment_method(self):
        return "CARD"
    
    
class ParkingLot:
    def __init__(self,spot_allocation_strategy: ParkingSpotAllocationStrategy, fee_strategy: ParkingFeeStrategy):
        self.floors=[]
        self.tickets={}
        self.next_ticket_id=1

        self.spot_allocation_strategy=spot_allocation_strategy
        self.fee_strategy=fee_strategy
    
        self.lock=threading.Lock()


    def build_floors(self,floor:ParkingFloor):
        self.floors.append(floor)

    def generate_ticket(self,vehicle,floor,spot):
        ticket_id=self.next_ticket_id
        self.next_ticket_id+=1

        ticket=Ticket(ticket_id,vehicle,floor, spot)

        self.tickets[ticket_id]=ticket

        return ticket
    def has_active_ticket(self, vehicle):
        for ticket in self.tickets.values():
            if (ticket.vehicle.vehicle_number == vehicle.vehicle_number
                    and ticket.ticket_status == TicketStatus.ACTIVE):
                return True
        return False

    def park_vehicle(self, vehicle: Vehicle):
        with self.lock:

            if self.has_active_ticket(vehicle):
                print("Vehicle is already parked")
                return None

            allocation= self.spot_allocation_strategy.allocate_spot(vehicle,self.floors)

            if allocation is None:
                print("No available slots")
                return None
            
            floor,spot=allocation

            if not spot.park(vehicle):
                return None

            floor.occupy_spot(spot)

            ticket= self.generate_ticket(vehicle, floor,spot)
            ticket.print_entry_ticket()
            return ticket
    
    def get_ticket(self, ticket_id):
        with self.lock:
            return self.tickets.get(ticket_id)
        
    def unpark_vehicle(self, ticket_id, payment_strategy, exit_time=None):
        with self.lock:
            ticket=self.tickets.get(ticket_id)
            if ticket is None:
                print("Invalid Ticket")
                return None

            if ticket.ticket_status != TicketStatus.ACTIVE:
                print("Ticket is already processed")
                return None

            ticket.exit_time=exit_time or datetime.now()

            ticket.amount=self.fee_strategy.calculate_fee(ticket)

        payment_status=payment_strategy.pay(ticket.amount)

        if payment_status!=PaymentStatus.SUCCESSFUL:
            ticket.ticket_status=TicketStatus.ACTIVE
            return None

        with self.lock:
            if ticket.ticket_status != TicketStatus.ACTIVE:
                return None

            if not ticket.spot.unpark(ticket.vehicle):
                print("Unable to release parking spot")
                return None
            
            ticket.floor.release_spot(ticket.spot)   

            ticket.ticket_status=TicketStatus.CLOSED
            ticket.print_exit_ticket(payment_strategy.get_payment_method())
            

        return ticket.amount
 
class EntryGate:
    def __init__(self,id, parking_lot: ParkingLot):
        self.id=id
        self.parking_lot=parking_lot

    def enter(self, vehicle: Vehicle):
        return self.parking_lot.park_vehicle(vehicle)

class ExitGate:
    def __init__(self,id, parking_lot:ParkingLot):
        self.id=id
        self.parking_lot=parking_lot

    def process_exit(self, ticket_id, payment_strategy):
        return self.parking_lot.unpark_vehicle(ticket_id,payment_strategy)
        


if __name__=="__main__":
    allocation_strategy=FindAvailableSpotStrategy()
    fee_strategy=SimpleFeeStrategy()

    lot=ParkingLot(allocation_strategy,fee_strategy)

    floor1=ParkingFloor(1)
    floor1.add_spots(ParkingSpot(1, SpotType.BIKE))
    floor1.add_spots(ParkingSpot(2, SpotType.COMPACT))
    floor1.add_spots(ParkingSpot(3, SpotType.LARGE))

    display_board=DisplayBoard()

    floor1.add_observer(display_board)

    lot.build_floors(floor1)

    entry_gate=EntryGate(1,lot)
    exit_gate=ExitGate(1,lot)

    car1=Vehicle(VehicleType.CAR,"KA-01-1234")
    car2 = Vehicle(VehicleType.CAR, "KA-01-4567")
    bike1 = Vehicle(VehicleType.BIKE,"KA-01-9876")
    truck1 = Vehicle(VehicleType.TRUCK,"KA-01-1111")

    print("\n--- CAR 1 ENTERING ---")
    ticket1 = entry_gate.enter(car1)
    print("\n--- CAR 2 ENTERING ---")
    ticket2 = entry_gate.enter(car2)
    print("\n--- BIKE 1 ENTERING ---")
    ticket3 = entry_gate.enter(bike1)
    print("\n--- TRUCK 1 ENTERING ---")
    ticket4 = entry_gate.enter(truck1)
    print("\n--- CAR 1 EXITING ---")
    exit_gate.process_exit(ticket1.ticket_id,UPIPayment())
    print("\n--- CAR 2 trying to ENTER again ---")
    ticket5 = entry_gate.enter(car2)

    car3 = Vehicle(VehicleType.CAR, "KA-01-9999")
    print("\n--- CAR 3 ENTERING AFTER CAR 1 EXIT ---")
    ticket6 = entry_gate.enter(car3)

# Output
# --- CAR 1 ENTERING ---
# Floor number:1
# Available spots: {'Bike': 1, 'Compact': 0, 'Large': 1}
#
# ========== ENTRY TICKET ==========
# Ticket ID    : 1
# Vehicle      : KA-01-1234
# Vehicle Type : Car
# Floor        : 1
# Spot         : 2
# Entry Time   : 2026-08-20 13:52:44.942460
# Status       : Active
# ====================================
#
# --- CAR 2 ENTERING ---
# Floor number:1
# Available spots: {'Bike': 1, 'Compact': 0, 'Large': 0}
# 
# ========== ENTRY TICKET ==========
# Ticket ID    : 2
# Vehicle      : KA-01-4567
# Vehicle Type : Car
# Floor        : 1
# Spot         : 3
# Entry Time   : 2026-08-20 13:52:44.943285
# Status       : Active
# ====================================
# 
# 
# --- BIKE 1 ENTERING ---
# Floor number:1
# Available spots: {'Bike': 0, 'Compact': 0, 'Large': 0}

# ========== ENTRY TICKET ==========
# Ticket ID    : 3
# Vehicle      : KA-01-9876
# Vehicle Type : Bike
# Floor        : 1
# Spot         : 1
# Entry Time   : 2026-08-20 13:52:44.943842
# Status       : Active
# ====================================
# 
# 
# --- TRUCK 1 ENTERING ---
# No available slots

# --- CAR 1 EXITING ---
# Paid 50 paid by UPI
# Floor number:1
# Available spots: {'Bike': 0, 'Compact': 1, 'Large': 0}

# ========== EXIT TICKET ==========
# Ticket ID    : 1
# Vehicle      : KA-01-1234
# Vehicle Type : Car
# Floor        : 1
# Spot         : 2
# Entry Time   : 2026-08-20 13:52:44.942460
# Exit Time    : 2026-08-20 13:52:44.944680
# Amount       : 50
# Payment      : UPI
# Status       : Closed
# =================================


# --- CAR 2 trying to ENTER again ---
# Vehicle is already parked

# --- CAR 3 ENTERING AFTER CAR 1 EXIT ---
# Floor number:1
# Available spots: {'Bike': 0, 'Compact': 0, 'Large': 0}

# ========== ENTRY TICKET ==========
# Ticket ID    : 4
# Vehicle      : KA-01-9999
# Vehicle Type : Car
# Floor        : 1
# Spot         : 2
# Entry Time   : 2026-08-20 13:52:44.945660
# Status       : Active
# ====================================