import os
import requests

def check_ollama_availability():
    """Check if the Ollama server is available."""
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=3)
        if response.status_code == 200:
            print(f"🟢 Ollama server is available at {ollama_url}.")
            return True
        else:
            print(f"⚠️ Ollama server returned status {response.status_code} at {ollama_url}.")
            return False
    except requests.RequestException as e:
        print(f"⚠️ Ollama server is not available at {ollama_url}: {str(e)}")
        return False


# Mock database: list of flights
flights = [
    {"flight_number": "NY100", "origin": "New York", "destination": "London", "time": "2025-05-01 08:00", "airline": "Global Airways"},
    {"flight_number": "LA200", "origin": "Los Angeles", "destination": "Tokyo", "time": "2025-05-01 10:30", "airline": "Pacific Routes"},
    {"flight_number": "CH300", "origin": "Chicago", "destination": "Paris", "time": "2025-05-01 15:45", "airline": "Euro Connect"},
    {"flight_number": "SF400", "origin": "San Francisco", "destination": "Sydney", "time": "2025-05-01 23:15", "airline": "Ocean Pacific"},
    {"flight_number": "MI500", "origin": "Miami", "destination": "Rio de Janeiro", "time": "2025-05-02 07:30", "airline": "South American Airways"}
]

def search_flights(origin=None, destination=None, flight_number=None, airline=None):
    """
    Search for flights based on exact matches for origin, destination, flight number, or airline.
    Ensures that at least one valid filter is applied.
    """
    print(f"🔍 Searching for: Origin={origin}, Destination={destination}, Flight Number={flight_number}, Airline={airline}")

    # If flight number is provided, prioritize searching by flight number only
    if flight_number:
        matches = [flight for flight in flights if flight["flight_number"].lower() == flight_number.lower()]
        print(f"🔍 Flight number search results: {matches}")
        return matches

    # If no flight number, apply standard search
    if not any([origin, destination, airline]):
        print("⚠️ No valid search parameters provided. Returning an empty list.")
        return []

    # Normalize input (convert to lowercase)
    origin = origin.lower() if origin else None
    destination = destination.lower() if destination and destination != "city name" else None  # Ignore "City Name"
    airline = airline.lower() if airline else None

    # Filter flights with exact matching for provided fields
    matches = [
        flight for flight in flights
        if (not origin or flight["origin"].lower() == origin)
        and (not destination or flight["destination"].lower() == destination)
        and (not airline or flight["airline"].lower() == airline)
    ]

    print(f"🔍 Found flights: {matches}")
    return matches

if __name__ == "__main__":
    # Example search
    result = search_flights("Chicago")
    print(result)
