import os
import json
import requests
from langchain_ollama import OllamaLLM
from typing import Tuple, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set default Ollama settings
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2:latest")  # Use default if not set

if not OLLAMA_MODEL:
    print("❌ OLLAMA_MODEL is missing! Using default model: 'llama2:latest'.")

# Initialize Ollama LLM
def initialize_ollama():
    """Initialize the Ollama LLM model safely."""
    try:
        ollama_llm = OllamaLLM(model=OLLAMA_MODEL)
        print(f"🟢 Successfully initialized Ollama LLM with model: {OLLAMA_MODEL}")
        return ollama_llm
    except Exception as e:
        print(f"❌ Failed to initialize Ollama LLM: {str(e)}")
        return None

ollama_llm = initialize_ollama()

def check_ollama_availability() -> Tuple[bool, str]:
    """Check if the locally running Ollama server is available."""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        if response.status_code == 200:
            return True, "🟢 Ollama server is available"
        return False, f"❌ Ollama server returned status code: {response.status_code}"
    except requests.exceptions.Timeout:
        return False, "⚠️ Ollama server timeout. It may be overloaded or down."
    except requests.exceptions.ConnectionError:
        return False, "❌ Cannot connect to Ollama server. Ensure it is running."
    except Exception as e:
        return False, f"⚠️ Error checking Ollama server: {str(e)}"

def generate_fallback_response(query: str, flights: List[dict]) -> str:
    """Generate a simple response when Ollama is not available."""
    if not flights:
        return "I couldn't find any flights matching your criteria. Please try again with different details."

    response = "Here are the flights that match your search:\n\n"
    for flight in flights:
        response += (
            "✈️ Flight {flight_number} from {origin} to {destination}\n"
            "⏰ Time: {time}\n"
            "🏢 Airline: {airline}\n\n"
        ).format(
            flight_number=flight.get("flight_number", "Unknown"),
            origin=flight.get("origin", "Unknown"),
            destination=flight.get("destination", "Unknown"),
            time=flight.get("time", "N/A"),
            airline=flight.get("airline", "N/A")
        )
    return response.strip()

def generate_response(query: str, flights: List[dict]) -> str:
    """Generate a natural language response using the LangChain Ollama integration."""
    is_available, message = check_ollama_availability()
    if not is_available:
        print(f"⚠️ {message}")
        return generate_fallback_response(query, flights)

    if not ollama_llm:
        print("⚠️ Ollama model is not initialized. Using fallback response.")
        return generate_fallback_response(query, flights)

    try:
        if flights:
            flight_info = json.dumps(flights, indent=2)
            prompt = f"""
            User Query: {query}

            Available Flights:
            {flight_info}

            Generate a natural language response summarizing these flights, including flight number, time, and airline details.
            """
        else:
            prompt = f"""
            User Query: {query}

            No matching flights found. Please provide a response indicating this politely.
            """

        print("🟢 Sending prompt to Ollama for response generation...")
        response = ollama_llm.invoke(prompt)
        return response.strip() if response else generate_fallback_response(query, flights)

    except Exception as e:
        print(f"⚠️ Ollama LLM generation failed: {str(e)}")
        return generate_fallback_response(query, flights) + f" (⚠️ Error: {str(e)})"

# Test
if __name__ == "__main__":
    test_flights = [
        {"flight_number": "NY100", "origin": "New York", "destination": "London", "time": "2025-05-01 08:00", "airline": "Global Airways"}
    ]
    print(generate_response("flights from New York", test_flights))

