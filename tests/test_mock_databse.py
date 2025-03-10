import unittest
from unittest.mock import patch
import os
import requests
from mock_database import flights, search_flights, check_ollama_availability

class TestMockDatabase(unittest.TestCase):
    def test_flight_data_exists(self):
        self.assertGreater(len(flights), 0, "Flight database should not be empty")
    
    def test_flight_structure(self):
        self.assertEqual(len(flights), 5, "Expected exactly 5 flights")
        expected_keys = {"flight_number", "origin", "destination", "time", "airline"}
        for flight in flights:
            self.assertEqual(set(flight.keys()), expected_keys, "Flight data has incorrect structure")
            self.assertIsInstance(flight["flight_number"], str, "Flight number should be a string")
            self.assertNotEqual(flight["origin"], flight["destination"], "Origin and destination should differ")

    def test_search_flights_by_flight_number(self):
        results = search_flights(flight_number="NY100")
        self.assertEqual(len(results), 1, "Should find exactly one flight for NY100")
        self.assertEqual(results[0]["flight_number"], "NY100", "Flight NY100 should be found")

    def test_search_flights_by_origin(self):
        results = search_flights(origin="New York")
        self.assertEqual(len(results), 1, "Should find exactly one flight from New York")
        self.assertTrue(all(f["origin"] == "New York" for f in results), "All results should have origin New York")

    def test_search_flights_by_destination(self):
        results = search_flights(destination="London")
        self.assertEqual(len(results), 1, "Should find exactly one flight to London")
        self.assertTrue(all(f["destination"] == "London" for f in results), "All results should have destination London")

    def test_search_flights_by_airline(self):
        results = search_flights(airline="Global Airways")
        self.assertEqual(len(results), 1, "Should find exactly one flight by Global Airways")
        self.assertTrue(all(f["airline"] == "Global Airways" for f in results), "All results should have airline Global Airways")

    def test_search_flights_combined_filters(self):
        results = search_flights(origin="San Francisco", destination="Sydney")
        self.assertEqual(len(results), 1, "Should find exactly one flight from San Francisco to Sydney")
        self.assertEqual(results[0]["flight_number"], "SF400", "Flight SF400 should be found")

    def test_search_flights_no_results(self):
        results = search_flights(flight_number="XYZ999")
        self.assertEqual(len(results), 0, "Should return no results for invalid flight number")

    def test_search_flights_no_parameters(self):
        results = search_flights()
        self.assertEqual(len(results), 0, "Should return no results when no parameters provided")

    def test_search_flights_case_insensitivity(self):
        results = search_flights(flight_number="ny100")
        self.assertEqual(len(results), 1, "Should find NY100 regardless of case")
        self.assertEqual(results[0]["flight_number"], "NY100", "Flight NY100 should be found")

    def test_search_flights_ignore_city_name(self):
        results = search_flights(destination="City Name")
        self.assertEqual(len(results), 0, "Should ignore 'City Name' as destination")

    @patch("requests.get")
    def test_check_ollama_availability_success(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        self.assertTrue(check_ollama_availability(), "Should return True when Ollama is available")

    @patch("requests.get")
    def test_check_ollama_availability_failure(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.status_code = 500
        self.assertFalse(check_ollama_availability(), "Should return False on server error")

    @patch("requests.get")
    def test_check_ollama_availability_exception(self, mock_get):
        mock_get.side_effect = requests.RequestException("Connection error")
        self.assertFalse(check_ollama_availability(), "Should return False on exception")

if __name__ == "__main__":
    unittest.main()