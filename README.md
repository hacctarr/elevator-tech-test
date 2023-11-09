# README for Elevator Simulation Application

## Overview

This Python application simulates an elevator system in a building. The simulation includes a set of classes to model passengers, elevators, and the system itself. It features the ability to generate random calls to the elevator with varying numbers of passengers and floors.

## Features

- **Passenger Simulation**: Passengers are simulated with a start floor and destination floor, along with tracking their wait and ride times.
- **Elevator Operations**: Elevators can move between floors, pick up passengers, and drop them off at their destination floors.
- **Elevator System Management**: Manages multiple elevators and processes passenger calls in a queued manner.
- **Statistical Analysis**: Post-simulation, it can report various statistics like average wait time, ride time, and total time for all passengers.
- **Random Call Generation**: The simulation can generate random calls to the elevator at random times with a number of passengers chosen according to a lognormal distribution.
- **Reproducibility**: By seeding the random number generator, the simulation can be reproduced with identical outcomes for the same inputs.

## Installation

To run the elevator simulation, you need Python installed on your system. This application has been developed and tested with Python 3.x. Additionally, NumPy is used for generating random numbers and distributions.

1. Clone the repository or download the source code.
2. Install NumPy if you haven't already:

```sh
pip install numpy
```

## Usage

1. Import the `ElevatorSystem` and `Passenger` classes in your Python script:

```python
from elevator_simulation import ElevatorSystem, Passenger
```

2. Initialize the elevator system:

```python
elevator_system = ElevatorSystem(num_elevators=3, num_floors=100)
```

3. Generate calls and run the simulation (an example function for generating random calls is provided):

```python
simulate_elevator_calls(elevator_system, duration=10000, total_calls=500, seed=42)
```

4. After running the simulation, retrieve statistics:

```python
stats = elevator_system.stats()
print(stats)
```

5. You can create passengers manually and call the elevator:

```python
passenger = Passenger(start_floor=1, destination_floor=10)
elevator_system.call_elevator(passenger)
```

6. Run the elevator system for a set number of steps:

```python
elevator_system.run(num_steps=10000)
```

## Disclaimer

This application is a simulation and should not be used for real-world elevator system design or management without proper expertise and further development.

## Contact

For support or to report issues, please file an issue on the project's issue tracker on GitHub.