"""
================================================================================
LLD: Elevator System
================================================================================

Functional Requirement:
1. user request destination for elevator outside (floor 2-- go to up/down) and also inside the  elevator(inside: take me to floor 10)
2. it should support multiple request calls 
3. open and close door
4. incase of emergency- alarm and safe methods
5. display board should display the state of elevator (which floor, direction - coming up or down,)

Non Functional Requirement:
1. concurrency / thready safety
2. no duplicate calls 
3. incase of issue

Core entities
UserRequest
    - floor 
    - direction  (based on inside/outside)

Elevator
    - curr_floor
    - Direction
    - Elevator_State
    - door_state
    - requests=[]

    - open_door()
    - close_door()
    - request() --(from inside we can select floor_number)
    - run() --- move up.down
    - start_elevator()
    - stop_elevator()
    - display_board()-- observer design pattern

ElevatorSystem
    - Elevators=[]
    - FindNearestAvailableStrategy - get_elevator()
    - assign_request_elevator()
    
for concurrency/lock we can do it in elevatorsystem

Identify relationship:
Elevator runs around each floor
we can have a elevator system which maintains/has a elevator

ElevatorSystem
    receives request
          ↓
FindNearestAvailableStrategy
    selects elevator
          ↓
Elevator
    handles the request

"""
#Coding

from abc import ABC, abstractmethod
from enum import Enum
import threading
import time

class Direction(Enum):
    UP = "Up"
    DOWN = "Down"
    IDLE = "Idle"

class ElevatorState(Enum):
    MOVING = "Moving"
    STOPPED="Stopped"
    IDLE = "Idle"

class DoorState(Enum):
    OPEN="Open"
    CLOSED="Closed"

class UserRequest:
    def __init__(self,floor, direction=None):
        self.floor=floor
        self.direction=direction

class RequestSchedulingStrategy(ABC):
    @abstractmethod
    def get_next_request(self,elevator):
        pass

class SimpleElevatorSchedulingStrategy(RequestSchedulingStrategy):
    def get_next_request(self, elevator):

        if not elevator.requests:
            return None
        
        # If elevator is already at a requested floor, service that request first.
        for request in elevator.requests:
            if request.floor == elevator.curr_floor:
                return request

        # Elevator is idle -> take first request
        if elevator.direction == Direction.IDLE:
            request=elevator.requests[0]

            if request.floor > elevator.curr_floor:
                elevator.direction = Direction.UP

            elif request.floor < elevator.curr_floor:
                elevator.direction =  Direction.DOWN

            return request

        # Elevator is moving UP
        if elevator.direction == Direction.UP:
            # requests=[3 5 8]  curr_floor=2
            up_request=[request for request in elevator.requests if request.floor>elevator.curr_floor] 
            if up_request:
                return min(up_request, key=lambda request:request.floor)
            else:
                elevator.direction = Direction.DOWN
                return self.get_next_request(elevator)

        # Elevator is moving DOWN
        if elevator.direction == Direction.DOWN:
            # requests=[3 5 8]  curr_floor=7
            down_request=[request for request in elevator.requests if request.floor<elevator.curr_floor]
            if down_request:
                return max(down_request, key=lambda request:request.floor)
            else:
                elevator.direction = Direction.UP
                return self.get_next_request(elevator)


class Elevator:
    def __init__(self,elevator_id,curr_floor, scheduling_strategy: RequestSchedulingStrategy):
        self.elevator_id=elevator_id
        self.curr_floor=curr_floor
        self.elevator_state=ElevatorState.IDLE
        self.direction=Direction.IDLE
        self.door_state=DoorState.CLOSED

        self.requests=[]
        self.observers=[]

        self.scheduling_strategy =  scheduling_strategy

        self.lock=threading.Lock()
        self.running=True
        self.thread=threading.Thread(target=self.run,daemon=True)
        self.thread.start()

        

    def add_request(self,request):
        with self.lock:
             # Avoid duplicate requests
            for existing in self.requests:
                if existing.direction ==  request.direction and existing.floor == request.floor:
                    return
            self.requests.append(request)

    def select_floor(self, floor):
        self.add_request(UserRequest(floor))

    def get_current_floor(self):
        with self.lock:
            return self.curr_floor

    def is_idle(self):
        with self.lock:
            return self.elevator_state==ElevatorState.IDLE

    def open_door(self):
        self.door_state=DoorState.OPEN
        print(F"Elevator {self.elevator_id} arrived at floor {self.curr_floor}, doors open")

    def close_door(self):
        self.door_state=DoorState.CLOSED
        print(F"Elevator {self.elevator_id} closed at floor {self.curr_floor}")

    def has_requests(self):
        with self.lock:
            return bool(self.requests)

    def run(self):
        while self.running:
            self.move()
            time.sleep(0.5)

    def stop(self):
        self.running = False
        self.thread.join()
        print(f"Elevator {self.elevator_id} stopped.")


    def move(self):
        should_notify = False

        with self.lock:
            request=self.scheduling_strategy.get_next_request(self)

            # No requests -> elevator becomes idle
            if request is None:
                if self.direction!=Direction.IDLE:
                    self.direction = Direction.IDLE
                    self.elevator_state = ElevatorState.IDLE
                    should_notify = True

            else:
                target_floor=request.floor

                # Move UP
                if self.curr_floor<target_floor:
                    self.direction=Direction.UP
                    self.elevator_state=ElevatorState.MOVING
                    self.curr_floor+=1
                    should_notify = True

                # Move DOWN
                elif self.curr_floor>target_floor:
                    self.direction=Direction.DOWN
                    self.elevator_state=ElevatorState.MOVING
                    self.curr_floor-=1
                    should_notify = True

                # Reached target floor
                else:
                    self.elevator_state = ElevatorState.STOPPED
                    # Request has been serviced
                    self.requests.remove(request)

                    self.open_door()   
                    self.close_door()

                    # No more requests
                    if not self.requests:
                        self.direction = Direction.IDLE
                        self.elevator_state = ElevatorState.IDLE
                    should_notify = True    

        # Don't notify observers while holding the lock
        if should_notify:
            self.notify_observer()

    def add_observer(self,observer):
        if observer not in self.observers:
            self.observers.append(observer)

    def notify_observer(self):
        for observer in self.observers:
            observer.update(self.elevator_id,self.curr_floor,self.direction)
 
class Observer(ABC):
    @abstractmethod
    def update(self,elevator_id,floor,direction):
        pass            

class DisplayBoard(Observer):
    def update(self,elevator_id,floor,direction):
        print(f"Elevator {elevator_id} is at Floor number: {floor}, going {direction.value}")

class ElevatorRequestStrategy(ABC):
    @abstractmethod
    def get_elevator(self,request,elevators):
        pass

class FindNearestAvailableStrategy(ElevatorRequestStrategy):
    def get_elevator(self,request: UserRequest, elevators: list["Elevator"]):
            best_elevator =None
            best_distance =float('inf')
            for elevator in elevators:
                floor=elevator.get_current_floor()
                idle=elevator.is_idle()
                if not idle:
                    continue

                distance=abs(floor - request.floor)

                if distance<best_distance :
                    best_distance =distance
                    best_elevator=elevator

            return best_elevator
    
class ElevatorSystem:
    def __init__(self,elevators:list[Elevator], elevator_request_strategy: ElevatorRequestStrategy):
        self.elevator_request_strategy=elevator_request_strategy
        self.elevators=elevators

    def assign_request_elevator(self,request: UserRequest):
        elevator=self.elevator_request_strategy.get_elevator(request,self.elevators)
        if elevator is None:
            print("No elevator available")
            return None
        
        elevator.add_request(request)
        
        return elevator

def main():
    scheduling_strategy=SimpleElevatorSchedulingStrategy()

    elevator1 =  Elevator(elevator_id=1, curr_floor=0, scheduling_strategy=scheduling_strategy)
    elevator2 = Elevator(elevator_id=2, curr_floor=0, scheduling_strategy=scheduling_strategy)

    display=DisplayBoard()

    elevator1.add_observer(display)
    elevator2.add_observer(display)

    request_strategy = FindNearestAvailableStrategy()

    system = ElevatorSystem([elevator1,elevator2],request_strategy)

    # --------------------------------------------------------
    # 1. Outside request - User is at floor 2 and wants to go UP
    # --------------------------------------------------------
    print("\n--- TEST 1: Outside request ---")
    elevator = system.assign_request_elevator(UserRequest(2, Direction.UP))

    # Give elevator some time to reach floor 2
    time.sleep(2)
    # --------------------------------------------------------
    # 2. Multiple Inside request -  User enters the SAME elevator and selects floor 10
    # --------------------------------------------------------
    print("\n--- TEST 2: Multiple inside requests ---")
    elevator.select_floor(8)
    elevator.select_floor(5)
    elevator.select_floor(10)

    time.sleep(7)
    # Expected:
    # Elevator should process:
    # 5 -> 8 -> 10
    # depending on current direction/scheduling strategy.

    # =========================================================
    # TEST 3: Multiple OUTSIDE + INSIDE requests
    # =========================================================
    print("\n--- TEST 3: Multiple inside + outside requests ---")

    # Two outside requests -> two elevators
    elevator_a = system.assign_request_elevator( UserRequest(3, Direction.UP))
    elevator_b = system.assign_request_elevator(UserRequest(9, Direction.DOWN))

    # Inside requests for the assigned elevators
    if elevator_a:
        elevator_a.select_floor(7)
        elevator_a.select_floor(10)

    if elevator_b:
        elevator_b.select_floor(5)
        elevator_b.select_floor(1)

    time.sleep(12)

    # =========================================================
    # TEST 4: Duplicate request
    # =========================================================
    print("\n--- TEST 4: Duplicate request ---")

    system.assign_request_elevator(UserRequest(6, Direction.UP))
    system.assign_request_elevator(UserRequest(6, Direction.UP))

    time.sleep(5)

    # Shutdown
    elevator1.stop()
    elevator2.stop()


if __name__=="__main__":
    main()
