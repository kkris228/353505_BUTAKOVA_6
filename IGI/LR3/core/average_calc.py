"""
Task 2: Calculate average 
Version: 1.0
Author: Butakova Kristina
Date: 16.04.2025
"""

def calculate_average_until_zero() -> tuple:
    """
    Accepts integers from user input until 0 is entered.
    Returns:
        tuple: (count, total_sum, average)
    """
    total = 0
    count = 0

    while True:
        try:
            num = int(input("Enter an integer (0 to stop): "))
            if num == 0:
                break
            total += num
            count += 1
        except ValueError:
            print("Invalid input. Please enter an integer.")

    average = total / count if count > 0 else 0.0
    return count, total, average
