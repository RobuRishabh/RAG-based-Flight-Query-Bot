import os
import json
import requests
from langchain_ollama import OllamaLLM  # Correct import
from typing import Tuple, List
from dotenv import load_dotenv

load_dotenv()
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2:latest")

def initialize_ollama():
    try:
        ollama_llm = OllamaLLM(model=OLLAMA_MODEL, base_url=OLLAMA_URL)
        print(f"🟢 Successfully initialized Ollama LLM with model: {OLLAMA_MODEL}")
        return ollama_llm
    except Exception as e:
        print(f"❌ Failed to initialize Ollama LLM: {str(e)}")
        return None

ollama_llm = initialize_ollama()

def check_ollama_availability() -> Tuple[bool, str]:
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        return response.status_code == 200, f"🟢 Ollama server is available at {OLLAMA_URL}"
    except requests.RequestException as e:
        return False, f"⚠️ Ollama server is not available at {OLLAMA_URL}: {str(e)}"

def generate_fallback_response(query: str, flights: List[dict]) -> str:
    if not flights:
        return "I couldn't find any flights matching your criteria. Please try again."
    response = "Here are the flights that match your search:\n\n"
    for flight in flights:
        response += (
            f"✈️ Flight {flight.get('flight_number', 'Unknown')} from {flight.get('origin', 'Unknown')} to {flight.get('destination', 'Unknown')}\n"
            f"⏰ Time: {flight.get('time', 'N/A')}\n"
            f"🏢 Airline: {flight.get('airline', 'N/A')}\n\n"
        )
    return response.strip()

def generate_response(query: str, flights: List[dict]) -> str:
    is_available, message = check_ollama_availability()
    if not is_available or not ollama_llm:
        print(f"⚠️ {message if not is_available else 'Ollama model not initialized'}")
        return generate_fallback_response(query, flights)

    try:
        flight_info = json.dumps(flights, indent=2) if flights else "No matching flights found."
        prompt = f"""
        User Query: {query}
        Available Flights: {flight_info}
        Generate a natural language response summarizing these flights, including flight number, time, and airline details if available, or politely indicate no flights were found.
        """
        print("🟢 Sending prompt to Ollama for response generation...")
        response = ollama_llm.invoke(prompt)
        return response.strip() if response else generate_fallback_response(query, flights)
    except Exception as e:
        print(f"⚠️ Ollama LLM generation failed: {str(e)}")
        return generate_fallback_response(query, flights)

# Test
if __name__ == "__main__":
    test_flights = [
        {"flight_number": "NY100", "origin": "New York", "destination": "London", "time": "2025-05-01 08:00", "airline": "Global Airways"}
    ]
    print(generate_response("flights from New York", test_flights))

