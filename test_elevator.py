import unittest
from elevator import Elevator, ElevatorSystem, Passenger
from simulator import Passenger

class TestElevator(unittest.TestCase):

    def setUp(self):
        self.elevator_system = ElevatorSystem(num_floors=5, num_elevators=1)
        self.elevator = self.elevator_system.elevators[0]

    def test_pick_up(self):
        # Test picking up a passenger
        passenger = Passenger(start_floor=1, destination_floor=2)
        self.elevator_system.call_elevator(passenger)
        self.elevator.pick_up(passenger)
        self.assertIn(passenger, self.elevator.passengers)
        self.assertIn(passenger.destination_floor, self.elevator.destination_floors)

        # Test picking up a passenger when the elevator is full
        for i in range(10):
            passenger = Passenger(start_floor=1, destination_floor=4)
            self.elevator_system.call_elevator(passenger)
            self.elevator.pick_up(passenger)
        passenger = Passenger(start_floor=1, destination_floor=5)
        self.elevator_system.call_elevator(passenger)
        self.assertFalse(self.elevator.pick_up(passenger))
        self.assertNotIn(passenger, self.elevator.passengers)
        self.assertNotIn(passenger.destination_floor, self.elevator.destination_floors)

    def test_drop_off_passengers(self):
        # Test dropping off a passenger
        passenger = Passenger(start_floor=1, destination_floor=2)
        self.elevator_system.call_elevator(passenger)
        self.elevator.pick_up(passenger)
        self.elevator.current_floor = 2
        self.assertTrue(self.elevator.drop_off_passengers())
        self.assertNotIn(passenger, self.elevator.passengers)
        self.assertNotIn(passenger.destination_floor, self.elevator.destination_floors)

        # Test dropping off multiple passengers
        for i in range(4):
            passenger = Passenger(start_floor=1, destination_floor=i+2)
            self.elevator_system.call_elevator(passenger)
            self.elevator.pick_up(passenger)
        self.elevator.current_floor = 4
        self.assertTrue(self.elevator.drop_off_passengers())
        self.assertEqual(len(self.elevator.passengers), 3)
        self.assertIn(5, self.elevator.destination_floors)

    def test_check_for_pickups(self):
        # Test picking up a passenger on the same floor
        self.elevator.current_floor = 1
        self.elevator.moving_direction = 1
        self.elevator.passengers = []
        passenger = Passenger(start_floor=1, destination_floor=2)
        self.elevator_system.call_elevator(passenger)
        self.assertTrue(self.elevator.check_for_pickups())
        self.assertIn(passenger, self.elevator.passengers)
        self.assertIn(passenger.destination_floor, self.elevator.destination_floors)

        # Test not picking up a passenger going in the opposite direction
        self.elevator.destination_floors.remove(2)
        passenger = Passenger(start_floor=1, destination_floor=2)
        self.elevator_system.call_elevator(passenger)
        self.elevator.moving_direction = -1
        self.assertFalse(self.elevator.check_for_pickups())
        self.assertNotIn(passenger, self.elevator.passengers)
        self.assertNotIn(passenger.destination_floor, self.elevator.destination_floors)

        # Test not picking up a passenger on a different floor
        passenger = Passenger(start_floor=2, destination_floor=3)
        self.elevator_system.call_queue.append(passenger)
        self.assertFalse(self.elevator.check_for_pickups())
        self.assertNotIn(passenger, self.elevator.passengers)
        self.assertNotIn(passenger.destination_floor, self.elevator.destination_floors)

    def test_step(self):
        # Test moving up
        elevator_system = ElevatorSystem(num_floors=5, num_elevators=1)
        passenger = Passenger(start_floor=2, destination_floor=3)
        elevator_system.call_elevator(passenger)
        self.assertIsNone(passenger.elevator)
        self.assertEqual(elevator_system.elevators[0].current_floor, 1)
        self.assertFalse(elevator_system.elevators[0].is_door_open)
        self.assertEqual(elevator_system.elevators[0].door_timer, 0)
        elevator_system.step()
        self.assertIsNone(passenger.elevator)
        self.assertEqual(elevator_system.elevators[0].current_floor, 2)
        self.assertFalse(elevator_system.elevators[0].is_door_open)
        self.assertEqual(elevator_system.elevators[0].door_timer, 0)
        elevator_system.step()
        self.assertEqual(elevator_system.elevators[0], passenger.elevator)
        self.assertTrue(elevator_system.elevators[0].is_door_open)
        self.assertEqual(elevator_system.elevators[0].door_timer, 5)
        elevator_system.step()
        elevator_system.step()
        elevator_system.step()
        elevator_system.step()
        elevator_system.step()
        self.assertEqual(elevator_system.elevators[0].door_timer, 0)
        self.assertEqual(passenger.current_floor, 3)

        # Test moving down
        passenger = Passenger(start_floor=3, destination_floor=2)
        self.elevator_system.call_elevator(passenger)
        self.elevator.current_floor = 3
        self.elevator.moving_direction = -1
        self.elevator.step()
        self.elevator.door_timer = 0
        self.elevator.step()
        self.assertEqual(self.elevator.current_floor, 2)

        # Test opening doors
        passenger = Passenger(start_floor=2, destination_floor=3)
        self.elevator_system.call_elevator(passenger)
        self.elevator.current_floor = 2
        self.elevator.step()
        self.assertTrue(self.elevator.is_door_open)

        # Test closing doors
        self.elevator.door_timer = 1
        self.elevator.step()
        self.assertFalse(self.elevator.is_door_open)

class TestPassenger(unittest.TestCase):

    def test_init(self):
        p = Passenger(start_floor=1, destination_floor=5)
        self.assertEqual(p.start_floor, 1)
        self.assertEqual(p.destination_floor, 5)
        self.assertEqual(p.current_floor, 1)
        self.assertEqual(p.wait_time, 0)
        self.assertEqual(p.ride_time, 0)
        self.assertIsNone(p.elevator)

    def test_step(self):
        p = Passenger(start_floor=1, destination_floor=5)
        p.step()
        self.assertEqual(p.wait_time, 1)
        self.assertEqual(p.ride_time, 0)
        self.assertIsNone(p.elevator)

        p.elevator = True
        p.step()
        self.assertEqual(p.wait_time, 1)
        self.assertEqual(p.ride_time, 1)
        self.assertIsNotNone(p.elevator)

        p.elevator = None
        p.current_floor = p.destination_floor
        p.step()
        self.assertEqual(p.wait_time, 1)
        self.assertEqual(p.ride_time, 1)
        self.assertIsNone(p.elevator)

    def test_total_time(self):
        p = Passenger(start_floor=1, destination_floor=5)
        p.wait_time = 5
        p.ride_time = 10
        self.assertEqual(p.total_time, 15)

if __name__ == '__main__':
    unittest.main()