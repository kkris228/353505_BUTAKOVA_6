"""
Task 3: Calculate number of characters excluding spaces
Version: 1.0
Author: Butakova Kristina
Date: 16.04.2025
"""
def count_non_space_characters() -> int:
    """
    Count all characters in the string except for spaces.
    
    Returns:
        int: Number of characters excluding spaces.
    """
    user_input = input("Enter a text: ")  
    count = 0  

    for char in user_input:
        if char != " ": 
            count += 1
    
    return count