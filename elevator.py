from collections import deque

DOOR_TIME = 5  # time to open doors at each floor
LOBBY_TIME = 30  # time to open doors at lobby
ELEVATOR_CAPACITY = 10  # max number of passengers in an elevator

class Passenger:
    """A class representing a passenger in the elevator system."""
    elevator = None
    def __init__(self, start_floor, destination_floor):
        """
        Initialize a new Passenger object.

        Args:
            start_floor (int): The floor the passenger is starting from.
            destination_floor (int): The floor the passenger wants to go to.
        """
        self.start_floor = start_floor
        self.destination_floor = destination_floor
        self.current_floor = start_floor
        self.wait_time = 0  # Time spent waiting for the elevator
        self.ride_time = 0  # Time spent inside the elevator

    def step(self):
        """
        Update the passenger's wait time or ride time, depending on whether they are in the elevator or not.
        """
        if self.elevator:
            self.ride_time += 1
        elif self.elevator is None and self.current_floor != self.destination_floor:
            self.wait_time += 1

    @property
    def total_time(self):
        """
        Calculate the total time spent by the passenger.

        Returns:
            int: The total time spent by the passenger.
        """
        return self.wait_time + self.ride_time

class Elevator:
    """
    A class representing an elevator in the elevator system.
    """
    def __init__(self, elevator_system, elevator_id, num_floors):
        """
        Initialize a new Elevator object.

        Args:
            elevator_system (ElevatorSystem): The elevator system that the elevator belongs to.
            elevator_id (int): The ID of the elevator.
            num_floors (int): The number of floors in the building.
        """
        self.elevator_system = elevator_system
        self.elevator_id = elevator_id
        self.num_floors = num_floors

        self.is_door_open = False
        self.door_timer = 0  # time to next action (move or close door)
        self.current_floor = 1 if self.elevator_id % 2 == 0 else self.num_floors
        self.passengers = []
        self.destination_floors = set()
        self.moving_direction = 0  # -1 for down, 0 for idle, 1 for up
        
        self.time_in_operation = 0  # total time in operation
        self.passengers_served = 0  # total passengers served
        self.stops_made = 0  # total stops

    def step(self):
        """
        Update the state of the elevator for one time step.
        """
        self.time_in_operation += 1
        if self.door_timer > 0:
            self.door_timer -= 1

        did_drop_off = 0

        # Remove the floor from destinations if we've arrived
        if self.current_floor in self.destination_floors:
            did_drop_off = self.drop_off_passengers()

        if self.current_floor == self.num_floors:
            self.moving_direction = -1
        elif self.current_floor == 1:
            self.moving_direction = 1

        # Before moving, check if we can pick up any passengers
        did_pick_up = self.check_for_pickups()

        # If the door was closed and we should it, set the timer to close it
        if not self.is_door_open and (did_drop_off or did_pick_up):
            self.stops_made += 1
            self.is_door_open = True
            self.door_timer = LOBBY_TIME if self.current_floor == 1 else DOOR_TIME

        # Elif we can move
        if self.door_timer == 0:
            self.is_door_open = False

            if not self.destination_floors:
                if self.current_floor == self.num_floors:
                    self.destination_floors.add(1)
                    self.moving_direction = -1
                elif self.current_floor == 1:
                    self.destination_floors.add(self.num_floors)
                    self.moving_direction = 1
                elif self.elevator_id % 2 == 0:
                    self.destination_floors.add(1)
                    self.moving_direction = -1
                else:
                    self.destination_floors.add(self.num_floors)
                    self.moving_direction = 1
            # # Move the elevator one floor in its current direction
            next_floor = self.current_floor + self.moving_direction
            if 1 <= next_floor <= self.num_floors:
                self.current_floor = next_floor
            else:
                self.moving_direction = 0
            for passenger in self.passengers:
                passenger.current_floor = self.current_floor

    def check_for_pickups(self):
        """
        Check if there are any passengers waiting on the current floor to go in the same direction as the elevator.

        Returns:
            bool: True if the elevator should open its doors, False otherwise.
        """
        did_pick_up = 0
        for passenger in list(self.elevator_system.calls.get(self.current_floor, [])):
            if (    ((self.moving_direction >= 0 and passenger.destination_floor > self.current_floor) or
                     (self.moving_direction <= 0 and passenger.destination_floor < self.current_floor))):
                if self.pick_up(passenger):
                    self.moving_direction = 1 if passenger.destination_floor > self.current_floor else -1
                    did_pick_up += 1
                else:
                    break
        return did_pick_up

    def pick_up(self, passenger):
        """
        Add a passenger to the elevator if there is room.

        Args:
            passenger (Passenger): The passenger to add to the elevator.

        Returns:
            bool: True if the passenger was added, False otherwise.
        """
        if len(self.passengers) < ELEVATOR_CAPACITY:
            passenger.elevator = self
            self.passengers.append(passenger)
            self.destination_floors.add(passenger.destination_floor)
            self.elevator_system.calls[self.current_floor].remove(passenger)
            self.passengers_served += 1
            return True
        return False

    def drop_off_passengers(self):
        """
        Drop off any passengers whose destination is the current floor.

        Returns:
            bool: True if any passengers were dropped off, False otherwise.
        """
        did_drop_off = 0
        for passenger in list(self.passengers):  # Make a copy of the list to modify it while iterating
            if passenger.destination_floor == self.current_floor:
                passenger.current_floor = self.current_floor
                passenger.elevator = None
                self.passengers.remove(passenger)
                did_drop_off += 1
        self.destination_floors.remove(self.current_floor)
        return did_drop_off

class ElevatorSystem:
    """
    A class representing an elevator system.

    Attributes:
        num_floors (int): The number of floors in the building.
        elevators (list): A list of Elevator objects in the system.
        calls (deque): A queue of passengers waiting for the elevator.
        passengers (list): A list of all passengers that have used the system.
        current_time (int): The current time in the system.
    """
    def __init__(self, num_elevators, num_floors):
        self.num_floors = num_floors
        self.elevators = [Elevator(self, i, num_floors) for i in range(num_elevators)]
        self.calls = {}  # Queues for passengers waiting for the elevator
        self.passengers = []  # All passengers that have used the system
        self.current_time = 0

    def call_elevator(self, passenger):
        """
        A passenger calls an elevator.

        Args:
            passenger (Passenger): The passenger calling the elevator.
        """
        queue = self.calls.get(passenger.start_floor, None)
        if queue is None:
            self.calls[passenger.start_floor] = deque()
        self.calls.get(passenger.start_floor).append(passenger)
        self.passengers.append(passenger)

    def step(self):
        """
        Update the system by one time-step.
        """
        self.current_time += 1
        for elevator in self.elevators:
            elevator.step()
        for passenger in self.passengers:
            passenger.step()

    def run(self, num_steps):
        # Run the system for a given number of time steps
        for _ in range(num_steps):
            self.step()

    def stats(self):
        """
        Calculate and return system statistics.

        Returns:
            dict: A dictionary containing the following statistics:
                - average_wait_time: The average wait time for passengers.
                - average_ride_time: The average ride time for passengers.
                - average_total_time: The average total time (wait time + ride time) for passengers.
                - max_wait_time: The maximum wait time for passengers.
                - min_wait_time: The minimum wait time for passengers.
                - elevators: A list of dictionaries containing statistics for each elevator in the system.
        """
        # Calculate and return system statistics
        wait_times = [p.wait_time for p in self.passengers]
        ride_times = [p.ride_time for p in self.passengers]
        total_times = [p.total_time for p in self.passengers]
        elevators = [{
                str(elevator.elevator_id): {
                    'passengers_served': elevator.passengers_served,
                    'time_in_operation':elevator.time_in_operation,
                    'stops_made':elevator.stops_made,
                }
            } for elevator in self.elevators]
        return {
            'average_wait_time': sum(wait_times) / len(wait_times) if wait_times else 0,
            'average_ride_time': sum(ride_times) / len(ride_times) if ride_times else 0,
            'average_total_time': sum(total_times) / len(total_times) if total_times else 0,
            'max_wait_time': max(wait_times) if wait_times else 0,
            'min_wait_time': min(wait_times) if wait_times else 0,
            'elevators': elevators,
        }

if __name__ == '__main__':
    # Example usage:
    elevator_system = ElevatorSystem(num_elevators=3, num_floors=100)
    # You would then call elevator_system.call_elevator(passenger) for each passenger
    # Finally, run the simulation for a given number of steps and print stats
    elevator_system.run(num_steps=10000)
    print(elevator_system.stats())
