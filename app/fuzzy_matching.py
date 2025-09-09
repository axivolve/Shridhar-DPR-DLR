from rapidfuzz import process
from typing import Dict, Any, Union, List


def get_best_fuzzy_matches(user_query: str, search_dict: Dict[str, Union[str, List[str]]], limit: int = 5) -> Dict[str, str]:
    """
    Find the best fuzzy matches for a user query in a dictionary.
    
    Args:
        user_query (str): The search query from the user
        search_dict (Dict[str, Union[str, List[str]]]): Dictionary to search in (searches values, returns keys)
                                                        Supports both string values and list values (uses first element)
        limit (int): Number of best matches to return (default: 5)
    
    Returns:
        Dict[str, str]: Dictionary with the best matching key-value pairs
        
    Examples:
        >>> # String format
        >>> search_data = {"A": "Villa 101", "B": "Villa 102", "C": "Security"}
        >>> result = get_best_fuzzy_matches("security", search_data, limit=3)
        >>> print(result)
        {"C": "Security"}
        
        >>> # List format  
        >>> search_data = {"8": ["Carpenter"], "9": ["Barbender"], "10": ["Mason"]}
        >>> result = get_best_fuzzy_matches("carpenter", search_data, limit=3)
        >>> print(result)
        {"8": "Carpenter"}
    """
    
    # Convert user query to lowercase for better matching
    query_lower = user_query.lower()
    
    # Normalize the dictionary - extract string values from both formats
    normalized_dict = {}
    for k, v in search_dict.items():
        if isinstance(v, list):
            # For list format, take the first element if it exists and is not empty
            if v and len(v) > 0 and v[0] and str(v[0]).strip():
                normalized_dict[k] = str(v[0]).strip()
        elif isinstance(v, str):
            # For string format, use directly if not empty
            if v and v.strip():
                normalized_dict[k] = v.strip()
    
    if not normalized_dict:
        return {}
    
    # Create choices list with lowercase values for matching
    choices = [v.lower() for v in normalized_dict.values()]
    
    # Get the best matches using rapidfuzz
    matches = process.extract(query_lower, choices, limit=limit)
    
    # Build simple result dictionary
    result = {}
    keys_list = list(normalized_dict.keys())
    values_list = list(normalized_dict.values())
    
    for match_value, score, match_index in matches:
        original_key = keys_list[match_index]
        original_value = values_list[match_index]
        result[original_key] = original_value
    
    return result
