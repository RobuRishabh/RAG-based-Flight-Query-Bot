from ollama_api import check_ollama_availability, generate_response

# Test Ollama server availability
is_available, message = check_ollama_availability()
print(f"Server Availability: {message}")

# Example query and flight data to test generate_response function
query = "What are the flights from New York to London?"
flights = [
    {"flight_number": "NY100", "origin": "New York", "destination": "London", "time": "2025-05-01 08:00", "airline": "Global Airways"},
    {"flight_number": "NY200", "origin": "New York", "destination": "London", "time": "2025-05-02 12:00", "airline": "Air London"}
]

# Test generating a response based on the query and flights
response = generate_response(query, flights)
print(f"Generated Response: \n{response}")
