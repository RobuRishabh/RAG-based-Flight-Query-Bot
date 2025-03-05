import ollama
import json
import os
from dotenv import load_dotenv
from mock_database import search_flights_semantic

# Load environment variables
load_dotenv()
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2:latest")  # Load model dynamically

def check_ollama_availability():
    """
    Check if Ollama server is available.
    Returns: True if available, False otherwise.
    """
    import requests
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

OLLAMA_AVAILABLE = check_ollama_availability()

def extract_entities_llama2(query):
    """
    Uses Ollama to extract structured flight details.
    """
    if not OLLAMA_AVAILABLE:
        print("⚠️ Ollama server is not available. Using basic keyword search.")
        return {}

    print(f"🟢 Using Ollama model: {OLLAMA_MODEL}")  # Debugging to check model name

    prompt = f"""
    Extract structured information from the following query:

    Query: "{query}"

    Return a JSON object with the following fields:
    - origin
    - destination
    - flight_number
    - time
    - date
    - airline

    If a field is missing, set it to null.
    """

    try:
        print(f"🟢 Sending request to Ollama with model: {OLLAMA_MODEL}")  # Debugging
        response = ollama.chat(
            model=OLLAMA_MODEL.strip(),  # Ensure it's a clean string
            messages=[{"role": "user", "content": prompt}]
        )
        print(f"🟢 Ollama API Response: {response}")  # Debugging

        extracted = json.loads(response["message"]["content"])  # Convert response string into dictionary
        extracted_clean = {k: v for k, v in extracted.items() if v is not None}  # Remove null values

        print(f"🟢 Extracted Entities: {extracted_clean}")  # Debugging

        return extracted_clean

    except json.JSONDecodeError:
        print("⚠️ Ollama returned an invalid response. Using fallback search.")
        return {}

    except Exception as e:
        print(f"⚠️ Error during LLaMA 2 entity extraction: {e}")
        return {}


def process_query(query):
    """
    Process user query and return relevant flight information.

    Args:
        query (str): User's question

    Returns:
        tuple: (bool success, str message, list matching_flights)
    """
    try:
        print(f"🟢 Processing query: {query}")  # Debug print

        search_params = extract_entities_llama2(query)
        print(f"🟢 Extracted Search Params: {search_params}")  # Debug print

        if not search_params:
            return False, (
                "I couldn't understand your flight query. "
                "Try specifying origin, destination, time, or airline."
            ), []

        # Perform semantic search using extracted parameters
        matching_flights = search_flights_semantic(query)

        print(f"🟢 Matching Flights: {matching_flights}")  # Debug print

        if not matching_flights:
            return False, "No flights found matching your criteria.", []

        return True, "Here are the flights that match your criteria:", matching_flights

    except Exception as e:
        print(f"❌ Error in process_query: {str(e)}")  # Debug print
        return False, f"An error occurred while processing your query: {str(e)}", []
