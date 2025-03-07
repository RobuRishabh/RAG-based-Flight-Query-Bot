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

def search_flights(query):
    """Search for flights based on keywords in the query."""
    query_lower = query.lower()
    
    # Match flights by checking if the query is present in any flight attribute
    matches = [
        flight for flight in flights 
        if query_lower in flight["origin"].lower()
        or query_lower in flight["destination"].lower()
        or query_lower in flight["flight_number"].lower()
        or query_lower in flight["airline"].lower()
    ]
    
    return matches

if __name__ == "__main__":
    # Example search
    result = search_flights("Chicago")
    print(result)
