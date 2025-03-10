import pytest
import requests
from unittest.mock import patch, Mock
import os
from ollama_api import initialize_ollama, check_ollama_availability, generate_fallback_response, generate_response, ollama_llm

# Fixture to mock environment variables
@pytest.fixture
def mock_env():
    original_env = os.environ.copy()
    os.environ["OLLAMA_URL"] = "http://test:11434"
    os.environ["OLLAMA_MODEL"] = "llama2:test"
    yield
    os.environ.clear()
    os.environ.update(original_env)

# 1. Tests for initialize_ollama
@patch("ollama_api.OllamaLLM")
def test_initialize_ollama_success(mock_ollama, mock_env):
    mock_instance = Mock()
    mock_ollama.return_value = mock_instance
    result = initialize_ollama()
    assert result == mock_instance, "Should return OllamaLLM instance on success"
    mock_ollama.assert_called_once_with(model="llama2:test", base_url="http://test:11434")

@patch("ollama_api.OllamaLLM")
def test_initialize_ollama_failure(mock_ollama, mock_env):
    mock_ollama.side_effect = Exception("Connection failed")
    result = initialize_ollama()
    assert result is None, "Should return None on initialization failure"

# 2. Tests for check_ollama_availability
@patch("requests.get")
def test_check_ollama_availability_success(mock_get, mock_env):
    mock_response = mock_get.return_value
    mock_response.status_code = 200
    is_available, message = check_ollama_availability()
    assert is_available is True, "Should return True when server is available"
    assert "Ollama server is available" in message, "Should return success message"
    mock_get.assert_called_once_with("http://test:11434/api/tags", timeout=3)

@patch("requests.get")
def test_check_ollama_availability_failure(mock_get, mock_env):
    mock_get.side_effect = requests.RequestException("Connection error")
    is_available, message = check_ollama_availability()
    assert is_available is False, "Should return False on request exception"
    assert "Ollama server is not available" in message, "Should return error message"

# 3. Tests for generate_fallback_response
def test_generate_fallback_response_with_flights():
    flights = [
        {"flight_number": "NY100", "origin": "New York", "destination": "London", "time": "2025-05-01 08:00", "airline": "Global Airways"}
    ]
    result = generate_fallback_response("flights from New York", flights)
    assert "Flight NY100" in result, "Should include flight number"
    assert "New York to London" in result, "Should include origin and destination"
    assert "Time: 2025-05-01 08:00" in result, "Should include time"
    assert "Airline: Global Airways" in result, "Should include airline"

def test_generate_fallback_response_no_flights():
    result = generate_fallback_response("flights from Mars", [])
    assert "I couldn't find any flights" in result, "Should return no-flights message"

def test_generate_fallback_response_missing_fields():
    flights = [{"flight_number": "NY100"}]  # Missing other fields
    result = generate_fallback_response("test query", flights)
    assert "Flight NY100" in result, "Should include flight number"
    assert "Unknown to Unknown" in result, "Should handle missing origin/destination"
    assert "Time: N/A" in result, "Should handle missing time"
    assert "Airline: N/A" in result, "Should handle missing airline"

# 4. Tests for generate_response
@patch("ollama_api.check_ollama_availability")
@patch("ollama_api.ollama_llm.invoke")
def test_generate_response_ollama_success(mock_invoke, mock_check, mock_env):
    mock_check.return_value = (True, "Server available")
    mock_invoke.return_value = "Flight NY100 departs from New York to London at 08:00 with Global Airways."
    with patch("ollama_api.ollama_llm", Mock()):
        flights = [{"flight_number": "NY100", "origin": "New York", "destination": "London", "time": "2025-05-01 08:00", "airline": "Global Airways"}]
        result = generate_response("flights from New York", flights)
        assert "NY100" in result, "Should include flight details from Ollama"
        assert "New York to London" in result, "Should include route"
        mock_invoke.assert_called_once()

@patch("ollama_api.check_ollama_availability")
def test_generate_response_ollama_unavailable(mock_check, mock_env):
    mock_check.return_value = (False, "Server unavailable")
    flights = [{"flight_number": "NY100", "origin": "New York", "destination": "London"}]
    result = generate_response("flights from New York", flights)
    assert "Flight NY100" in result, "Should use fallback when Ollama unavailable"
    assert "New York to London" in result, "Should include route in fallback"

@patch("ollama_api.check_ollama_availability")
def test_generate_response_ollama_not_initialized(mock_check, mock_env):
    mock_check.return_value = (True, "Server available")
    with patch("ollama_api.ollama_llm", None):
        flights = [{"flight_number": "NY100"}]
        result = generate_response("test query", flights)
        assert "Flight NY100" in result, "Should use fallback when ollama_llm is None"

@patch("ollama_api.check_ollama_availability")
@patch("ollama_api.ollama_llm.invoke")
def test_generate_response_ollama_failure(mock_invoke, mock_check, mock_env):
    mock_check.return_value = (True, "Server available")
    mock_invoke.side_effect = Exception("LLM error")
    with patch("ollama_api.ollama_llm", Mock()):
        flights = [{"flight_number": "NY100"}]
        result = generate_response("test query", flights)
        assert "Flight NY100" in result, "Should use fallback on Ollama exception"