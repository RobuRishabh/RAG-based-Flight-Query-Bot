import json
import os
import re
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM
from mock_database import search_flights, check_ollama_availability

# Load environment variables
load_dotenv()
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:3b")
OLLAMA_AVAILABLE = check_ollama_availability()

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

CITY_MAPPING = {
    "ny": "New York",
    "la": "Los Angeles",
    "ch": "Chicago",
    "sf": "San Francisco",
    "mi": "Miami"
}

def extract_entities_ollama(query):
    """
    Uses Ollama to extract structured flight details from a query and ensures correct data mapping.
    If Ollama fails to extract an entity, fallback to a keyword-based search.
    """
    if not OLLAMA_AVAILABLE or not ollama_llm:
        print("⚠️ Ollama server is unavailable. Using basic keyword search.")
        return {}

    print(f"🟢 Using Ollama model: {OLLAMA_MODEL}")
    prompt = f"""
    Extract flight details from the following user query and return only valid JSON.
    Do not include any explanations, additional text, or markdown.

    Query: "{query}"

    The response should be in this exact JSON format:
    {{
      "origin": "City Name",
      "destination": "City Name",
      "flight_number": "Flight Number",
      "date": "YYYY-MM-DD",
      "airline": "Airline Name"
    }}

    If a value is missing, set it to `null`.
    """

    try:
        print(f"🟢 Sending request to Ollama for entity extraction...")
        response = ollama_llm.invoke(prompt)

        # Extract valid JSON from response
        json_match = re.search(r"\{.*\}", response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            extracted = json.loads(json_str)

            # Clean extracted values
            if extracted.get("destination") == "City Name":
                extracted["destination"] = None  # Ignore placeholder values
            if extracted.get("origin") == "NYC":
                extracted["origin"] = "New York"  # Map city codes to full names

            # If no flight number is extracted, try regex
            if not extracted.get("flight_number"):
                extracted["flight_number"] = extract_flight_number(query)

            extracted_clean = {k: v for k, v in extracted.items() if v}  # Remove None values
            print(f"🟢 Extracted Entities from Ollama: {extracted_clean}")
            return extracted_clean

        else:
            print(f"⚠️ No valid JSON found in response. Falling back to keyword search.")
            return extract_entities_from_keywords(query)

    except json.JSONDecodeError as jde:
        print(f"⚠️ JSONDecodeError: {jde}. Falling back to keyword search.")
        return extract_entities_from_keywords(query)
    except Exception as e:
        print(f"⚠️ Error during entity extraction: {e}. Falling back to keyword search.")
        return extract_entities_from_keywords(query)

def extract_flight_number(query):
    """
    Extracts a flight number from a query using regex.
    Flight numbers typically have a two-letter airline code followed by 3-4 digits (e.g., "NY100").
    """
    match = re.search(r"\b[A-Z]{2}\d{3,4}\b", query)
    return match.group(0) if match else None


def extract_entities_from_keywords(query):
    """
    Fallback function to extract entities from a query using simple keyword matching.
    """
    keywords = query.lower()

    cities = ["new york", "los angeles", "chicago", "san francisco", "miami", "paris", "tokyo", "london", "rio de janeiro", "sydney"]
    airlines = ["global airways", "pacific routes", "euro connect", "ocean pacific", "south american airways"]

    origin = next((city for city in cities if city in keywords), None)
    destination = None  # Can't always determine destination reliably from keywords
    flight_number_match = re.search(r"\b[A-Z]{2}\d{3,4}\b", query)  # Match flight numbers like "NY100"
    flight_number = flight_number_match.group(0) if flight_number_match else None
    airline = next((air for air in airlines if air in keywords), None)

    extracted = {
        "origin": origin,
        "destination": destination,
        "flight_number": flight_number,
        "airline": airline
    }

    extracted_clean = {k: v for k, v in extracted.items() if v}  # Remove None values
    print(f"🟢 Extracted Entities from Keywords: {extracted_clean}")
    return extracted_clean


def process_query(query):
    """
    Process user query and return relevant flight information.
    Uses Ollama for entity extraction instead of Transformers.
    """
    try:
        print(f"🟢 Processing query: {query}")

        # Extract structured entities using Ollama
        search_params = extract_entities_ollama(query)

        # Ensure extracted values are correct before searching
        origin = search_params.get("origin")
        destination = search_params.get("destination")
        flight_number = search_params.get("flight_number")
        airline = search_params.get("airline")

        print(f"🟢 Searching with extracted parameters: {search_params}")

        # Use extracted details for searching
        matching_flights = search_flights(origin, destination, flight_number, airline)

        if not matching_flights:
            return False, "⚠️ No flights found matching your criteria. Please try again with different details.", []

        return True, "Here are the flights that match your criteria:", matching_flights

    except ValueError as ve:
        print(f"❌ ValueError in process_query: {str(ve)}")
        return False, f"Invalid query format: {str(ve)}", []
    except Exception as e:
        print(f"❌ Unexpected error in process_query: {str(e)}")
        return False, f"An error occurred while processing your query: {str(e)}", []



# Test
if __name__ == "__main__":
    success, message, flights = process_query("Show me flights from New York to London on May 1st")
    print(f"Success: {success}, Message: {message}, Flights: {flights}")
