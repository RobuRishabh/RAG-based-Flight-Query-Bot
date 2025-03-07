import unittest
from mock_database import flights, search_flights, check_ollama_availability

class TestMockDatabase(unittest.TestCase):
    def test_flight_data_exists(self):
        self.assertGreater(len(flights), 0, "Flight database should not be empty")
    
    def test_flight_structure(self):
        flight = flights[0]
        expected_keys = {"flight_number", "origin", "destination", "time", "airline"}
        self.assertEqual(set(flight.keys()), expected_keys, "Flight data has incorrect structure")

    def test_search_flights_by_flight_number(self):
        results = search_flights(flight_number="NY100")  # Use keyword arg for flight_number
        self.assertGreater(len(results), 0, "Should find at least one matching flight")
        self.assertIn("NY100", [f["flight_number"] for f in results], "Flight NY100 should be found")
        self.assertEqual(len(results), 1, "Should find exactly one flight for NY100")

    def test_search_flights_by_origin(self):
        results = search_flights(origin="New York")
        self.assertGreater(len(results), 0, "Should find flights from New York")
        self.assertTrue(all(f["origin"] == "New York" for f in results), "All results should have origin New York")

    def test_search_flights_by_destination(self):
        results = search_flights(destination="London")
        self.assertGreater(len(results), 0, "Should find flights to London")
        self.assertTrue(all(f["destination"] == "London" for f in results), "All results should have destination London")

    def test_search_flights_by_airline(self):
        results = search_flights(airline="Global Airways")
        self.assertGreater(len(results), 0, "Should find flights by Global Airways")
        self.assertTrue(all(f["airline"] == "Global Airways" for f in results), "All results should have airline Global Airways")

    def test_search_flights_no_results(self):
        results = search_flights(flight_number="XYZ999")
        self.assertEqual(len(results), 0, "Should return no results for invalid flight number")

    def test_search_flights_no_parameters(self):
        results = search_flights()
        self.assertEqual(len(results), 0, "Should return no results when no parameters provided")

    def test_search_flights_case_insensitivity(self):
        results = search_flights(flight_number="ny100")
        self.assertGreater(len(results), 0, "Should find NY100 regardless of case")
        self.assertIn("NY100", [f["flight_number"] for f in results], "Flight NY100 should be found")

if __name__ == "__main__":
    unittest.main()