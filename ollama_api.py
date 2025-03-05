import os
import json
import requests
from langchain_ollama import OllamaLLM
from typing import Tuple, List
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

print(f"🟢 Loaded OLLAMA_MODEL from .env: {os.getenv('OLLAMA_MODEL')}")  # Debugging check


# ✅ Use environment variables dynamically
OLLAMA_URL = os.getenv("OLLAMA_URL")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
if not OLLAMA_MODEL:
    print("❌ OLLAMA_MODEL is missing! Check your .env file.")
    exit(1)

# ✅ Initialize Ollama LLM
ollama_llm = OllamaLLM(model=OLLAMA_MODEL)

def check_ollama_availability() -> Tuple[bool, str]:
    """
    Check if the locally running Ollama server is available.
    
    Returns:
        Tuple[bool, str]: (is_available, message)
    """
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)  # ✅ Use .env URL and set timeout
        if response.status_code == 200:
            return True, "Ollama server is available"
        return False, f"Ollama server returned status code: {response.status_code}"
    except requests.exceptions.Timeout:
        return False, "⚠️ Ollama server timeout. It may be overloaded or down."
    except requests.exceptions.ConnectionError:
        return False, "❌ Cannot connect to Ollama server. Ensure it is running."
    except Exception as e:
        return False, f"⚠️ Error checking Ollama server: {str(e)}"

def generate_fallback_response(query: str, flights: List[dict]) -> str:
    """
    Generate a simple response when Ollama is not available.
    
    Args:
        query (str): User's original question.
        flights (list): Matching flight information.
    
    Returns:
        str: Fallback response.
    """
    if not flights:
        return "I couldn't find any flights matching your criteria. Please try again with different details."

    response = "Here are the flights that match your search:\n\n"
    for flight in flights:
        response += (f"Flight {flight['flight_number']} from {flight['origin']} to {flight['destination']}\n"
                    f"Time: {flight['time']}\n"
                    f"Airline: {flight['airline']}\n\n")
    return response

def generate_response(query: str, flights: List[dict]) -> str:
    """
    Generate a natural language response using the LangChain Ollama integration.

    Args:
        query (str): User's original question.
        flights (list): Matching flight information.

    Returns:
        str: Generated response.
    """
    # ✅ First check if Ollama is available
    is_available, message = check_ollama_availability()
    if not is_available:
        return generate_fallback_response(query, flights)

    try:
        # ✅ Prepare flight information for LLM
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

        # ✅ Generate response using LangChain's Ollama LLM
        response = ollama_llm(prompt)
        return response.strip()

    except Exception as e:
        return generate_fallback_response(query, flights) + f" (⚠️ Error: {str(e)})"
