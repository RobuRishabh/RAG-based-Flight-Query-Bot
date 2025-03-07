import unittest
from unittest.mock import patch, Mock
from query_handler import process_query, extract_entities_ollama, extract_flight_number, extract_entities_from_keywords, OLLAMA_AVAILABLE

class TestQueryHandler(unittest.TestCase):
    def setUp(self):
        # Reset global ollama_llm for each test
        global ollama_llm
        ollama_llm = None

    @patch("query_handler.OllamaLLM")
    def test_extract_entities_ollama_success(self, mock_ollama_llm):
        mock_llm_instance = Mock()
        mock_llm_instance.invoke.return_value = '''
        {"origin": "New York", "destination": "London", "flight_number": "NY100", "date": "2025-05-01", "airline": "Global Airways"}
        '''
        mock_ollama_llm.return_value = mock_llm_instance
        global ollama_llm
        ollama_llm = mock_llm_instance  # Set global for OLLAMA_AVAILABLE check

        if OLLAMA_AVAILABLE:
            result = extract_entities_ollama("Show me flight NY100")
            self.assertEqual(result["origin"], "New York")
            self.assertEqual(result["flight_number"], "NY100")
            self.assertEqual(result["destination"], "London")
            self.assertEqual(result["date"], "2025-05-01")
            self.assertEqual(result["airline"], "Global Airways")

    @patch("query_handler.OllamaLLM")
    def test_extract_entities_ollama_fallback(self, mock_ollama_llm):
        mock_llm_instance = Mock()
        mock_llm_instance.invoke.side_effect = Exception("Ollama error")
        mock_ollama_llm.return_value = mock_llm_instance
        global ollama_llm
        ollama_llm = mock_llm_instance

        result = extract_entities_ollama("Show me flights from New York")
        self.assertEqual(result["origin"], "new york")  # From keyword fallback
        self.assertNotIn("destination", result)  # No destination in simple keyword match

    def test_extract_flight_number(self):
        self.assertEqual(extract_flight_number("Show me flight NY100"), "NY100")
        self.assertIsNone(extract_flight_number("Show me flights from New York"))

    def test_extract_entities_from_keywords(self):
        result = extract_entities_from_keywords("Flights from New York with Global Airways")
        self.assertEqual(result["origin"], "new york")
        self.assertEqual(result["airline"], "global airways")
        self.assertNotIn("destination", result)

        result = extract_entities_from_keywords("Flight NY100")
        self.assertEqual(result["flight_number"], "NY100")

        result = extract_entities_from_keywords("Random text")
        self.assertEqual(result, {})

    def test_process_query_success(self):
        success, message, flights = process_query("Show me flight NY100")
        self.assertTrue(success, "Query should succeed")
        self.assertEqual(message, "Here are the flights that match your criteria:")
        self.assertGreater(len(flights), 0, "Should return at least one flight")
        self.assertIn("NY100", [f["flight_number"] for f in flights])

    def test_process_query_no_results(self):
        success, message, flights = process_query("Show me flight XYZ999")
        self.assertFalse(success, "Query should fail for invalid flight")
        self.assertEqual(message, "⚠️ No flights found matching your criteria. Please try again with different details.")
        self.assertEqual(len(flights), 0, "Should return no flights")

    @patch("query_handler.OllamaLLM")
    def test_process_query_ollama_unavailable(self, mock_ollama_llm):
        mock_llm_instance = Mock()
        mock_llm_instance.invoke.side_effect = Exception("Ollama unavailable")
        mock_ollama_llm.return_value = mock_llm_instance
        global ollama_llm
        ollama_llm = mock_llm_instance

        success, message, flights = process_query("Flights from New York")
        self.assertTrue(success, "Query should succeed with keyword fallback")
        self.assertEqual(message, "Here are the flights that match your criteria:")
        self.assertGreater(len(flights), 0, "Should return flights from New York")

if __name__ == "__main__":
    unittest.main()