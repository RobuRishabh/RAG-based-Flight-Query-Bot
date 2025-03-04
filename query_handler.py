"""
Query Handler to process the queries from the user and etract the required information from the database.
"""
from mock_database import search_flights
import re

def parse_query(query):
    """"
    Parse user query to extract relevant search parameters

    Args: query (str): User query
    Returns: dict: Query parameters
    """
    query = query.lower()
    search_params = {}

    # Check for origin city
    origin_indicator = ["from", "originating", "origin", "out of", "departing from", "leaving from"]
    for indicator in origin_indicator:
        if indicator in query:
            parts = query.split(indicator, 1) # maximum split of 1
            if len(parts) > 1:
                potential_origin = parts[1].split()[0:2].strip()
                search_params["origin"] = " ".join(potential_origin).title()

    # Check for destination city
    dest_indicators = ["to", "arriving at", "going to"]
    for indicator in dest_indicators:
        if indicator in query:
            parts = query.split(indicator, 1)
            if len(parts) > 1:
                potential_dest = parts[1].split()[0:2]  # Assuming 2-word city names
                search_params["destination"] = " ".join(potential_dest).title()
                
    # Check for flight number (even if 'flight' isn't explicitly mentioned)
    flight_number_match = re.search(r'\b[A-Z]{2,4}\d{3,4}\b', query)  # Match patterns like 'NY100' or 'LA200'
    if flight_number_match:
        search_params["flight_number"] = flight_number_match.group(0).upper()
        
    return search_params

def process_query(query):
    """
    Process user query and return relevant flight information
    
    Args: query (str): User's question
    Returns: tuple: (bool success, str message, list matching_flights)
    """
    try:
        search_params = parse_query(query)
        
        if not search_params:
            return False, "I couldn't understand the flight details in your question. Please try asking about specific origins, destinations, or flight numbers.", []
            
        matching_flights = search_flights(search_params)
        
        if not matching_flights:
            return False, "No flights found matching your criteria.", []
            
        return True, "Found matching flights!", matching_flights
        
    except Exception as e:
        return False, f"An error occurred while processing your query: {str(e)}", []
