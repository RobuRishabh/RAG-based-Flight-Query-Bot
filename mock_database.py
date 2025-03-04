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

def search_flights(query_params):
    """
    Search for flights based on query parameters
    """
    results = []
    for flight in flights:
        matches = True
        for key, value in query_params.items():
            if key not in flight:
                matches = False
                break
            # Handle the exact matches 
            if value.lower() != flight[key].lower():
                matches = False
                break
        if matches:
            results.append(flight)
    return results