import numpy as np
import unittest
from simulator import generate_lognormal_passenger_counts, generate_random_calls, generate_uniform_calls_with_lognormal_passengers, Passenger

class TestElevator(unittest.TestCase):

    def test_generate_lognormal_passenger_counts(self):
        # Test with 0 calls
        self.assertTrue((generate_lognormal_passenger_counts(0) == np.array([])).all())

        # Test with 1 call
        self.assertTrue((generate_lognormal_passenger_counts(1) >= 1).all())
        self.assertTrue((generate_lognormal_passenger_counts(1) <= 5).all())

        # Test with 10 calls
        counts = generate_lognormal_passenger_counts(10)
        self.assertEqual(len(counts), 10)
        self.assertTrue((counts >= 1).all())
        self.assertTrue((counts <= 5).all())

        # Test with 1000 calls
        counts = generate_lognormal_passenger_counts(1000)
        self.assertEqual(len(counts), 1000)
        self.assertTrue((counts == 1).any())
        self.assertTrue((counts >= 1).all())
        self.assertTrue((counts <= 5).all())
        self.assertTrue((counts == 5).any())

    def test_generate_random_calls(self):
        # Test with 0 calls
        time_series = generate_random_calls(num_floors=5, duration=10, total_calls=0)
        self.assertEqual(len(time_series), 0)

        # Test with 1 call
        time_series = generate_random_calls(num_floors=5, duration=10, total_calls=1)
        self.assertEqual(len(time_series), 1)
        self.assertEqual(len(time_series.keys()), 1)
        self.assertEqual(len(time_series.values()), 1)
        self.assertIn(list(time_series.values())[0][0].destination_floor, range(1, 6))

        # Test with 10 calls
        time_series = generate_random_calls(num_floors=5, duration=100, total_calls=100)
        passengers = [passenger for passengers in time_series.values() for passenger in passengers]
        counts = [0, 0, 0, 0, 0, 0]
        for passenger in passengers:
            self.assertIn(passenger.destination_floor, range(1, 6))
            counts[passenger.destination_floor] += 1
        self.assertNotEqual(counts[5], 0)

    def test_generate_uniform_calls_with_lognormal_passengers(self):
        # Test with 0 calls
        time_series = generate_uniform_calls_with_lognormal_passengers(num_floors=5, duration=10, total_calls=0, passenger_counts=[])
        self.assertEqual(len(time_series), 0)

        # Test with 1 call
        time_series = generate_uniform_calls_with_lognormal_passengers(num_floors=5, duration=10, total_calls=1, passenger_counts=[1])
        # self.assertEqual(len(time_series), 1)
        self.assertIsInstance(list(time_series.values())[0][0], Passenger)
        self.assertIn(list(time_series.values())[0][0].start_floor, range(1, 6))
        self.assertIn(list(time_series.values())[0][0].destination_floor, range(1, 6))

        # Test with 10 calls
        passenger_counts = generate_lognormal_passenger_counts(10).tolist()
        time_series = generate_uniform_calls_with_lognormal_passengers(num_floors=5, duration=10, total_calls=10, passenger_counts=passenger_counts)
        for passengers in time_series.values():
            self.assertIsInstance(passengers[0], Passenger)
            self.assertIn(passengers[0].start_floor, range(1, 6))
            self.assertIn(passengers[0].destination_floor, range(1, 6))

        # Test with 1000 calls
        passenger_counts = generate_lognormal_passenger_counts(1000).tolist()
        time_series = generate_uniform_calls_with_lognormal_passengers(num_floors=5, duration=10, total_calls=1000, passenger_counts=passenger_counts)
        for passengers in time_series.values():
            self.assertIsInstance(passengers[0], Passenger)
            self.assertIn(passengers[0].start_floor, range(1, 6))
            self.assertIn(passengers[0].destination_floor, range(1, 6))

if __name__ == '__main__':
    unittest.main()
