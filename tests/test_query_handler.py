import pytest
from unittest.mock import patch, Mock
import os
from query_handler import (
    extract_entities_ollama, extract_flight_number, extract_entities_from_keywords,
    process_query, initialize_ollama, OLLAMA_AVAILABLE, ollama_llm
)
from mock_database import search_flights

# Fixture to mock environment variables
@pytest.fixture
def mock_env():
    original_env = os.environ.copy()
    os.environ["OLLAMA_MODEL"] = "llama2:test"
    yield
    os.environ.clear()
    os.environ.update(original_env)

# 1. Tests for initialize_ollama
@patch("query_handler.OllamaLLM")
def test_initialize_ollama_success(mock_ollama, mock_env):
    mock_instance = Mock()
    mock_ollama.return_value = mock_instance
    result = initialize_ollama()
    assert result == mock_instance, "Should return OllamaLLM instance on success"
    mock_ollama.assert_called_once_with(model="llama2:test")

@patch("query_handler.OllamaLLM")
def test_initialize_ollama_failure(mock_ollama, mock_env):
    mock_ollama.side_effect = Exception("Connection failed")
    result = initialize_ollama()
    assert result is None, "Should return None on initialization failure"

# 2. Tests for extract_entities_ollama
@patch("query_handler.ollama_llm.invoke")
def test_extract_entities_ollama_success(mock_invoke, mock_env):
    # Simulate Ollama response with valid JSON
    mock_invoke.return_value = '''
    {
      "origin": "New York",
      "destination": "London",
      "flight_number": null,
      "date": "2025-05-01",
      "airline": null
    }
    '''
    with patch("query_handler.OLLAMA_AVAILABLE", True), patch("query_handler.ollama_llm", Mock()):
        result = extract_entities_ollama("Flights from New York to London")
        assert result == {"origin": "New York", "destination": "London", "date": "2025-05-01"}, "Should extract and clean entities correctly"

@patch("query_handler.ollama_llm.invoke")
def test_extract_entities_ollama_flight_number_fallback(mock_invoke, mock_env):
    # Simulate Ollama missing flight number, fallback to regex
    mock_invoke.return_value = '''
    {
      "origin": "New York",
      "destination": "London",
      "flight_number": null,
      "date": null,
      "airline": null
    }
    '''
    with patch("query_handler.OLLAMA_AVAILABLE", True), patch("query_handler.ollama_llm", Mock()):
        result = extract_entities_ollama("Flight NY100 from New York")
        assert result == {"origin": "New York", "destination": "London", "flight_number": "NY100"}, "Should fallback to regex for flight number"

@patch("query_handler.extract_entities_from_keywords")
def test_extract_entities_ollama_unavailable(mock_keywords, mock_env):
    mock_keywords.return_value = {"origin": "Chicago"}
    with patch("query_handler.OLLAMA_AVAILABLE", False):
        result = extract_entities_ollama("Flights from Chicago")
        assert result == {"origin": "Chicago"}, "Should fallback to keywords when Ollama unavailable"
        mock_keywords.assert_called_once()

@patch("query_handler.ollama_llm.invoke")
def test_extract_entities_ollama_invalid_json(mock_invoke, mock_env):
    mock_invoke.return_value = "Invalid response"
    with patch("query_handler.OLLAMA_AVAILABLE", True), patch("query_handler.ollama_llm", Mock()), \
         patch("query_handler.extract_entities_from_keywords") as mock_keywords:
        mock_keywords.return_value = {"origin": "Miami"}
        result = extract_entities_ollama("Flights from Miami")
        assert result == {"origin": "Miami"}, "Should fallback to keywords on invalid JSON"

# 3. Tests for extract_flight_number
def test_extract_flight_number_success():
    result = extract_flight_number("Flight NY100 departs soon")
    assert result == "NY100", "Should extract flight number NY100"

def test_extract_flight_number_none():
    result = extract_flight_number("Flights from New York")
    assert result is None, "Should return None when no flight number present"

# 4. Tests for extract_entities_from_keywords
def test_extract_entities_from_keywords_basic():
    result = extract_entities_from_keywords("Flights from New York to London")
    assert result == {"origin": "new york", "destination": "london"}, "Should extract origin and destination"

def test_extract_entities_from_keywords_flight_number():
    result = extract_entities_from_keywords("Flight LA200 from Los Angeles")
    assert result == {"origin": "los angeles", "flight_number": "LA200"}, "Should extract flight number"

def test_extract_entities_from_keywords_airline():
    result = extract_entities_from_keywords("Global Airways flights from New York")
    assert result == {"origin": "new york", "airline": "global airways"}, "Should extract airline"

def test_extract_entities_from_keywords_none():
    result = extract_entities_from_keywords("Random text")
    assert result == {}, "Should return empty dict when no entities found"

# 5. Tests for process_query
@patch("query_handler.extract_entities_ollama")
@patch("mock_database.search_flights")
def test_process_query_success(mock_search, mock_extract):
    mock_extract.return_value = {"origin": "New York", "destination": "London"}
    mock_search.return_value = [{"flight_number": "NY100", "origin": "New York", "destination": "London"}]
    success, message, flights = process_query("Flights from New York to London")
    assert success is True, "Should succeed with valid query"
    assert "Here are the flights" in message, "Should return success message"
    assert len(flights) == 1, "Should return one flight"
    assert flights[0]["flight_number"] == "NY100", "Flight should match NY100"

@patch("query_handler.extract_entities_ollama")
@patch("mock_database.search_flights")
def test_process_query_no_flights(mock_search, mock_extract):
    mock_extract.return_value = {"origin": "Mars"}
    mock_search.return_value = []
    success, message, flights = process_query("Flights from Mars")
    assert success is False, "Should fail when no flights found"
    assert "No flights found" in message, "Should return no-flights message"
    assert flights == [], "Should return empty flight list"

@patch("query_handler.extract_entities_ollama")
def test_process_query_exception(mock_extract):
    mock_extract.side_effect = Exception("Unexpected error")
    success, message, flights = process_query("Flights from New York")
    assert success is False, "Should fail on exception"
    assert "An error occurred" in message, "Should return error message"
    assert flights == [], "Should return empty flight list"