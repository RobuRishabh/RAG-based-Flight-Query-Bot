import unittest
from query_handler import parse_query, search_flights

class TestQueryHandler(unittest.TestCase):
    def test_parse_query(self):
        query = "What flights are from New York to London?"
        result = parse_query(query)
        self.assertEqual(result["origin"], "New York")
        self.assertEqual(result["destination"], "London")

    def test_search_flights(self):
        query = {"origin": "New York", "destination": "London"}
        results = search_flights(query)
        self.assertGreater(len(results), 0, "Should find at least one matching flight")
        self.assertIn("NY100", [f["flight_number"] for f in results])

    def test_no_results(self):
        query = {"origin": "Mars", "destination": "Jupiter"}
        results = search_flights(query)
        self.assertEqual(len(results), 0, "Should return no results for invalid query")

if __name__ == "__main__":
    unittest.main()