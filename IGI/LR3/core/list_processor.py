"""
Task 5: Finds the index of the maximum element by absolute value and the sum of elements after the first positive number.
Version: 1.0
Author: Butakova Kristina
Date: 16.04.2025
"""
def get_float_input(prompt: str) -> float:
    """
    Get a valid floating-point number from the user.
    Keeps prompting until a valid number is entered.
    """
    while True:
        try:
            return float(input(prompt))  # Convert input to float
        except ValueError:
            print("Invalid input! Please enter a valid floating-point number.")


def find_max_element_and_sum_after_positive(numbers: list) -> tuple:
    """
    Finds the index of the maximum element by absolute value and the sum of elements after the first positive number.
    
    Returns:
        tuple: (index of max element by absolute value, sum of elements after the first positive number)
    """
    # Check if all elements are the same
    if all(num == numbers[0] for num in numbers):
        print("All numbers are identical.")
        return -1, 0  # No need to proceed further if all numbers are identical

    max_value = max(numbers, key=abs)  # Maximum element by absolute value
    max_index = numbers.index(max_value)  # Index of that element
    
    # Find the first positive element
    positive_found = False
    sum_after_positive = 0
    for i, num in enumerate(numbers):
        if num > 0 and not positive_found:
            positive_found = True  # First positive element found
            continue  # Skip the first positive number in summing
        elif positive_found:
            sum_after_positive += num
    
    return max_index, sum_after_positive


def print_list(numbers: list):
    """Print the list to the screen."""
    print("List of numbers:", numbers)