"""
Version: 1.0
Author: Butakova Kristina
Date: 16.04.2025
"""

from core.sin_calc import calculate_sin
from utils.float_input import get_float
from core.average_calc import calculate_average_until_zero
from core.text_analysis import count_non_space_characters
from core.text_processor import analyze_text
from core.list_processor import get_float_input, find_max_element_and_sum_after_positive, print_list
from utils.input_generator import generate_float_sequence


def run_task1():
    print("Task 1: sin(x) calculation via power series\n")

    x = get_float("Enter x: ")
    eps = get_float("Enter precision (eps): ")

    result = calculate_sin(x, eps)

    print("\nResult:")
    print("{:<10} {:<10} {:<20} {:<20} {:<10}".format("x", "n", "F(x)", "Math F(x)", "eps"))
    print("{:<10.5f} {:<10} {:<20.10f} {:<20.10f} {:<10.1e}".format(
        result["x"], result["n"], result["Fx"], result["MathFx"], eps
    ))

def run_task2():
    print("\nTask 2")
    count, total, avg = calculate_average_until_zero()
    print(f"Summary:")
    print(f"Count: {count}")
    print(f"Sum:   {total}")
    print(f"Avg:   {avg:.2f}")

def run_task3():
    print("\nTask 3:")
    non_space_count = count_non_space_characters()  
    print(f"Number of characters (excluding spaces): {non_space_count}")

def run_task4():
    
    print("\nTask 4:")
    count_vowel_ending, average_length, words_of_avg_length, words_every_fifth = analyze_text()

    print(f"Number of words ending with a vowel: {count_vowel_ending}")
    print(f"Average word length: {average_length}")
    
    if words_of_avg_length:
        print(f"Words with average length: {', '.join(words_of_avg_length)}")
    else:
        print(f"No words with length {average_length} characters.")
    
    print("Every 5th word:")
    print(", ".join(words_every_fifth))

def run_task5():

    print("\nTask 5:")
    # Input the length of the list
    length = int(get_float_input("Enter the length of the list: "))
    
    # Generate the sequence using the generator
    numbers = list(generate_float_sequence(length))  # Generate the sequence using the generator
    
    print("Generated list:")
    print_list(numbers)
    
    # Process the list
    max_index, sum_after_positive = find_max_element_and_sum_after_positive(numbers)
    
    if max_index != -1:
        # Print the results only if numbers are not identical
        print(f"Index of the maximum element by absolute value: {max_index}") 
        print(f"Sum of elements after the first positive number: {sum_after_positive}")


if __name__ == "__main__":
    #run_task1()
    #run_task2()
    #run_task3()
    #run_task4()
    run_task5()