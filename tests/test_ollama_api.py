import unittest
from unittest.mock import patch
from ollama_api import call_ollama_api

class TestOllamaAPI(unittest.TestCase):
    @patch("ollama_api.requests.post")
    def test_call_ollama_api_success(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"response": "Flight NY100 departs at 08:00."}
        query = "What are flights from New York to London?"
        flight_data = [{"flight_number": "NY100", "origin": "New York", "destination": "London", "time": "2025-05-01 08:00"}]
        response = call_ollama_api(query, flight_data)
        self.assertEqual(response, "Flight NY100 departs at 08:00.")

    @patch("ollama_api.requests.post")
    def test_call_ollama_api_failure(self, mock_post):
        mock_post.return_value.status_code = 500
        query = "What are flights from New York to London?"
        flight_data = [{"flight_number": "NY100", "origin": "New York", "destination": "London", "time": "2025-05-01 08:00"}]
        with self.assertRaises(Exception):
            call_ollama_api(query, flight_data)

if __name__ == "__main__":
    unittest.main()