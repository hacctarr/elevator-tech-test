from elevator import ElevatorSystem, Passenger
import numpy as np

def generate_lognormal_passenger_counts(calls):
    """
    The number of passengers per call is random according to a lognormal distribution,
    rounded to the nearest integer in the range (0, 5].
    """
    # Define mean and standard deviation for the lognormal distribution
    mean = 0.7
    sigma = 0.6
    # Generate lognormal distribution
    raw_distribution = np.random.lognormal(mean, sigma, calls)
    # Round to nearest integer
    rounded_data = np.round(raw_distribution)
    # Clip the values to be within the range (1, 5]
    return np.clip(rounded_data, 1, 5)

def generate_random_calls(num_floors, duration, total_calls):
    """
    Generate calls to the elevator from the lobby at random times with random number of passengers.
    """
    time_series = {}
    for _ in range(total_calls):
        call_time = np.random.randint(0, duration)  # Time at which the passengers call the elevator
        num_passengers = np.random.randint(1, 6)
        for _ in range(num_passengers):  # Number of passengers calling the elevator at this time
            passenger = Passenger(1, np.random.randint(2, num_floors))  # Destination floor is chosen randomly
            time_series.setdefault(call_time, []).append(passenger)  # Add the passenger to the time series
    return time_series

def generate_uniform_calls_with_lognormal_passengers(num_floors, duration, total_calls, passenger_counts):
    """
    Generates uniform distribution of number and frequency of calls to the elevator
    from non-lobby floors.
    """
    if num_floors < 2 or total_calls < 1:
        return {}
    calls_per_floor = 1 + (total_calls / (num_floors - 1))  # Uniform number of calls per floor
    call_interval = 1 + int(duration // calls_per_floor)  # Uniform time interval between calls

    time_series = {}
    start_time = 0
    for floor in range(2, num_floors):  # Start from floor 2 since floor 1 is the lobby
        start_time = np.random.randint(0, call_interval)  # Random start time
        # Generate calls at uniform intervals
        for call_time in range(start_time, duration, call_interval):
            # Number of passengers calling the elevator at this time
            num_passengers = int(passenger_counts.pop(0)) if len(passenger_counts)>0 else 0
            for _ in range(num_passengers):
                # Destination floor is chosen randomly
                passenger = Passenger(floor, np.random.randint(1, num_floors))
                # Add the passenger to the time series
                time_series.setdefault(call_time, []).append(passenger)
    return time_series



def simulate_elevator_calls(elevator_system, duration, total_calls, seed):
    """
    A simulator that generates the time series of elevator calls and runs the elevator system for the given duration.
    It uses the following assumptions when generating the inputs:
    1. Except for the lobby, all other floors have a uniform distribution of number and frequency of calls.
    2. The number of passengers per call is random according to a lognormal distribution, rounded to the nearest integer in the range (0, 5].
    3. The random functions should be seeded in such a way that the results of any run can be reproduced if the same seed is used.
    """
    np.random.seed(seed)
    num_floors = elevator_system.num_floors

    # Number of calls to the elevator from the lobby
    lobby_calls = np.random.randint(0, total_calls/2)
    # Number of calls to the elevator from non-lobby floors
    nonlobby_calls = total_calls - lobby_calls

    # Generate the time series of calls to the elevator from the lobby
    time_series = generate_random_calls(num_floors, duration, lobby_calls)

    # Generate and append the time series of calls to the elevator from non-lobby floors
    passenger_counts = generate_lognormal_passenger_counts(nonlobby_calls)
    passenger_counts = passenger_counts.tolist()
    time_series.update(generate_uniform_calls_with_lognormal_passengers(num_floors, duration, nonlobby_calls, passenger_counts))

    # Run the simulation
    for t in range(duration):
        if t in time_series:
            for passenger in time_series[t]:
                elevator_system.call_elevator(passenger)
        elevator_system.step()
    print("Total:", sum(len(time_series[t]) for t in time_series))

if __name__ == '__main__':
    # Run the elevator call simulation
    elevator_system = ElevatorSystem(num_elevators=12, num_floors=60)
    simulate_elevator_calls(elevator_system, duration=3600, total_calls=3600, seed=42)
    print(elevator_system.stats())
