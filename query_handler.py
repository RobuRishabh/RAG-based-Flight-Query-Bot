import ollama
import json
import os
import re
from dotenv import load_dotenv
from mock_database import search_flights, check_ollama_availability

# Load environment variables
load_dotenv()
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2:latest")  # Load model dynamically

OLLAMA_AVAILABLE = check_ollama_availability()

def extract_entities_llama2(query):
    """
    Uses Ollama to extract structured flight details from a query.
    Ensures the response is always valid JSON.
    """
    if not OLLAMA_AVAILABLE:
        print("⚠️ Ollama server is unavailable. Using basic keyword search.")
        return {}

    print(f"🟢 Using Ollama model: {OLLAMA_MODEL}")
    prompt = f'''
    Extract flight details from this user query and respond **only** in valid JSON.
    Do not include any extra text, explanations, or markdown.
    
    Query: "{query}"
    
    Example valid responses:
    {{"origin": "New York", "destination": "London", "flight_number": "AA123", "time": "10:00 AM", "date": "2025-05-01", "airline": "Global Airways"}}
    {{"origin": "Chicago", "destination": null, "flight_number": null, "time": null, "date": null, "airline": null}}

    If a value is missing, set it to `null`.
    
    '''

    try:
        print(f"🟢 Sending request to Ollama with model: {OLLAMA_MODEL}")
        response = ollama.chat(model=OLLAMA_MODEL.strip(), messages=[{"role": "user", "content": prompt}])
        content = response["message"]["content"].strip()

        # 🔍 Extract the valid JSON from the response
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)  # Extract JSON part
            extracted = json.loads(json_str)  # Convert to dictionary

            # 🛠️ Clean extracted data (remove placeholders)
            extracted_clean = {k: v for k, v in extracted.items() if v and v.lower() not in ["null", "none"]}

            print(f"🟢 Extracted Entities: {extracted_clean}")
            return extracted_clean

        else:
            print(f"⚠️ No valid JSON found in response. Raw response: {content}")
            return {}

    except json.JSONDecodeError as jde:
        print(f"⚠️ JSONDecodeError: {jde}. Raw response: {content}")
        return {}
    except Exception as e:
        print(f"⚠️ Error during entity extraction: {e}")
        return {}


def process_query(query):
    """
    Process user query and return relevant flight information.
    Uses keyword search if Ollama is unavailable.
    """
    try:
        print(f"🟢 Processing query: {query}")

        # Extract structured entities (if Ollama is available)
        search_params = extract_entities_llama2(query) if OLLAMA_AVAILABLE else {}

        # Perform a keyword-based search instead of semantic search
        if search_params:
            print(f"🟢 Searching with extracted parameters: {search_params}")
            matching_flights = search_flights(search_params.get("origin", "") or search_params.get("destination", ""))
        else:
            print("⚠️ No structured entities found. Performing direct keyword search.")
            matching_flights = search_flights(query)

        if not matching_flights:
            return False, "No flights found matching your criteria.", []

        return True, "Here are the flights that match your criteria:", matching_flights

    except ValueError as ve:
        print(f"❌ ValueError in process_query: {str(ve)}")
        return False, f"Invalid query format: {str(ve)}", []
    except Exception as e:
        print(f"❌ Unexpected error in process_query: {str(e)}")
        return False, f"An error occurred while processing your query: {str(e)}", []

# Test
if __name__ == "__main__":
    success, message, flights = process_query("Show me flight NY100")
    print(f"Success: {success}, Message: {message}, Flights: {flights}")
