import ollama
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

flights = [
    {
        "flight_number": "NY100",
        "origin": "New York",
        "destination": "London",
        "time": "2025-05-01 08:00",
        "airline": "Global Airways"
    },
    {
        "flight_number": "LA200",
        "origin": "Los Angeles",
        "destination": "Tokyo",
        "time": "2025-05-01 10:30",
        "airline": "Pacific Routes"
    },
    {
        "flight_number": "CH300",
        "origin": "Chicago",
        "destination": "Paris",
        "time": "2025-05-01 15:45",
        "airline": "Euro Connect"
    },
    {
        "flight_number": "SF400",
        "origin": "San Francisco",
        "destination": "Sydney",
        "time": "2025-05-01 23:15",
        "airline": "Ocean Pacific"
    },
    {
        "flight_number": "MI500",
        "origin": "Miami",
        "destination": "Rio de Janeiro",
        "time": "2025-05-02 07:30",
        "airline": "South American Airways"
    }
]

### ✅ Check if Ollama is Running Before Sending API Calls
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

### ✅ Lazy Embedding Generation with Error Handling
flight_embeddings = {}

def generate_embedding(text):
    """
    Generate text embeddings using Ollama's LLaMA2 API.
    Only calls Ollama if the server is running.
    """
    if not OLLAMA_AVAILABLE:
        print("⚠️ Ollama server is not available. Using fallback search.")
        return None

    try:
        response = ollama.embeddings(model="llama2:latest", prompt=text)
        return np.array(response["embedding"])
    except Exception as e:
        print(f"⚠️ Ollama embedding failed: {e}")
        return None

def get_flight_embedding(flight_number):
    """
    Retrieve or generate an embedding for a flight.
    """
    if flight_number in flight_embeddings:
        return flight_embeddings[flight_number]

    # Get flight details
    flight = next((f for f in flights if f["flight_number"] == flight_number), None)
    if not flight:
        return None

    text = f"{flight['origin']} {flight['destination']} {flight['airline']} {flight['time']}"
    embedding = generate_embedding(text)
    if embedding is not None:
        flight_embeddings[flight_number] = embedding
    return embedding

def search_flights_semantic(query):
    """
    Perform semantic search on flight records using cosine similarity.
    """
    print(f"🟢 Searching flights for: {query}")  # Debug print

    try:
        query_embedding = generate_embedding(query)

        similarities = {}
        for flight in flights:
            flight_num = flight["flight_number"]
            flight_embedding = get_flight_embedding(flight_num)

            if flight_embedding is not None:
                similarity_score = cosine_similarity([query_embedding], [flight_embedding])[0][0]
                similarities[flight_num] = similarity_score

        matching_flights = [flight for flight in flights if similarities.get(flight["flight_number"], 0) > 0.6]

        print(f"🟢 Flights Found: {matching_flights}")  # Debug print

        return matching_flights

    except Exception as e:
        print(f"❌ Error in search_flights_semantic: {str(e)}")  # Debug print
        return []