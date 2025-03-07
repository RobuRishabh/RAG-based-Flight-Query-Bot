import unittest
from mock_database import flights

class TestMockDatabase(unittest.TestCase):
    def test_flight_data_exists(self):
        self.assertGreater(len(flights), 0, "Flight database should not be empty")
    
    def test_flight_structure(self):
        flight = flights[0]
        expected_keys = {"flight_number", "origin", "destination", "time"}
        self.assertEqual(set(flight.keys()), expected_keys, "Flight data has incorrect structure")

if __name__ == "__main__":
    unittest.main()