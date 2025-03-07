import unittest
from unittest.mock import patch, Mock
from ollama_api import initialize_ollama, check_ollama_availability, generate_response, generate_fallback_response

class TestOllamaAPI(unittest.TestCase):
    def setUp(self):
        # Reset global ollama_llm for each test
        global ollama_llm
        ollama_llm = None

    @patch("ollama_api.OllamaLLM")
    def test_initialize_ollama_success(self, mock_ollama_llm):
        mock_llm_instance = Mock()
        mock_ollama_llm.return_value = mock_llm_instance
        result = initialize_ollama()
        self.assertIsNotNone(result, "Ollama LLM should initialize successfully")
        self.assertEqual(result, mock_llm_instance)

    @patch("ollama_api.OllamaLLM", side_effect=Exception("Initialization failed"))
    def test_initialize_ollama_failure(self, mock_ollama_llm):
        result = initialize_ollama()
        self.assertIsNone(result, "Ollama LLM should return None on failure")

    @patch("ollama_api.requests.get")
    def test_check_ollama_availability_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        is_available, message = check_ollama_availability()
        self.assertTrue(is_available, "Ollama should be available")
        self.assertIn("available", message)

    @patch("ollama_api.requests.get", side_effect=requests.RequestException("Connection error"))
    def test_check_ollama_availability_failure(self, mock_get):
        is_available, message = check_ollama_availability()
        self.assertFalse(is_available, "Ollama should not be available")
        self.assertIn("not available", message)

    def test_generate_fallback_response_with_flights(self):
        flights = [
            {"flight_number": "NY100", "origin": "New York", "destination": "London", "time": "2025-05-01 08:00", "airline": "Global Airways"}
        ]
        response = generate_fallback_response("test query", flights)
        self.assertIn("NY100", response)
        self.assertIn("New York", response)
        self.assertIn("London", response)
        self.assertIn("2025-05-01 08:00", response)
        self.assertIn("Global Airways", response)

    def test_generate_fallback_response_no_flights(self):
        response = generate_fallback_response("test query", [])
        self.assertEqual(response, "I couldn't find any flights matching your criteria. Please try again.")

    @patch("ollama_api.check_ollama_availability")
    @patch("ollama_api.ollama_llm", new=Mock(invoke=lambda x: "Flight NY100 departs at 08:00 from New York to London with Global Airways"))
    def test_generate_response_success(self, mock_check_availability):
        mock_check_availability.return_value = (True, "Ollama available")
        query = "Show me flight NY100"
        flight_data = [
            {"flight_number": "NY100", "origin": "New York", "destination": "London", "time": "2025-05-01 08:00", "airline": "Global Airways"}
        ]
        response = generate_response(query, flight_data)
        self.assertIn("NY100", response)
        self.assertIn("08:00", response)
        self.assertIn("New York", response)
        self.assertIn("London", response)
        self.assertIn("Global Airways", response)

    @patch("ollama_api.check_ollama_availability")
    def test_generate_response_no_flights(self, mock_check_availability):
        mock_check_availability.return_value = (True, "Ollama available")
        # Ensure ollama_llm is initialized (mock it globally)
        global ollama_llm
        ollama_llm = Mock(invoke=lambda x: "No flights found.")
        query = "Show me flight XYZ999"
        flight_data = []
        response = generate_response(query, flight_data)
        self.assertEqual(response, "I couldn't find any flights matching your criteria. Please try again.")

    @patch("ollama_api.check_ollama_availability")
    def test_generate_response_ollama_unavailable(self, mock_check_availability):
        mock_check_availability.return_value = (False, "Ollama not available")
        query = "Show me flight NY100"
        flight_data = [
            {"flight_number": "NY100", "origin": "New York", "destination": "London", "time": "2025-05-01 08:00", "airline": "Global Airways"}
        ]
        response = generate_response(query, flight_data)
        self.assertIn("NY100", response)
        self.assertIn("New York", response)
        self.assertIn("London", response)

if __name__ == "__main__":
    unittest.main()