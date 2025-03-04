"""
Integration with the Ollama API for natural language generation.
"""
import os
import json
import requests
from dotenv import load_dotenv
from typing import Tuple, List

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL")
if not OLLAMA_URL:
    raise ValueError("OLLAMA_URL environment variable is not set.")
MODEL = os.getenv("OLLAMA_MODEL", "llama2")

def check_ollama_availability() -> Tuple[bool, str]:
    """
    Check if the Ollama server is available by querying its health endpoint.
    Returns: Tuple[bool, str]: (success, message)    
    """
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags")
        if response.status_code == 200:
            return True, "Ollama server is available."
        return False, "Ollama server is not available. status code: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Ollama server is not available. Connection error."
    except Exception as e:
        return False, f"An error occurred while checking Ollama availability: {str(e)}"
    
def generate_fallback_response(query:str, flights:List[dict]) -> str:
    """
    Generate a simple response when Ollama is not available.
    Args: query (str): User's question
          flights (List[dict]): List of matching flights
    Returns: str: Fallback response
    """
    if not flights:
        return "No flights found matching your criteria."
    
    response = "Here are the flights that match your criteria:\n"
    for flight in flights:
        response += f"Flight {flight['flight_number']} from {flight['origin']} to {flight['destination']} on {flight['time']} by {flight['airline']}\n"
    return response
 
def generate_response(query: str, flights: List[dict]) -> str:
    """
    Generate a natural language response using the Ollama model.
    Args: query (str): User's question
            flights (List[dict]): List of matching flights
    Returns: str: Natural language response
    """
    # Check is ollama server is available
    is_available, message = check_ollama_availability()
    if not is_available:
        return generate_fallback_response(query, flights)
    try:
        # Prepare the prompt for Ollama model
        if flights:
            flight_info = json.dumps(flights, indent = 2)
            prompt = f"""
            User Question: {query}

            Available Flights Information:
            {flight_info}
            Please provide a concise, natural language response that summarizes these flights, including flight numbers, times, and destinations.
            """
        else:
            prompt = f"""
            User Question: {query}

            No flights found matching your criteria.
            """
        # Make the api call to Ollama
        response = requests.post(f"{OLLAMA_URL}/api/generate", 
                                 json={
                                    "model": MODEL, 
                                    "prompt": prompt,
                                    "stream": False}, 
                                    timeout=10 # Timeout after 10 seconds
                                )
        if response.status_code == 200:
            try:
                response_data = response.json()
                return response_data.get("response", "Sorry, I couldn't generate a response.")
            except ValueError:
                return "There was an error processing the response from the server."
        else:
            return generate_fallback_response(query, flights)

    except requests.exceptions.RequestException as e:
        return generate_fallback_response(query, flights) + f" Error: {str(e)}"
    except Exception as e:
        return generate_fallback_response(query, flights) + f" Unexpected error: {str(e)}"
