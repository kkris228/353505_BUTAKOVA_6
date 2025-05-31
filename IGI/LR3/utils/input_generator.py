
def generate_float_sequence(length: int) -> iter:
    """
    Generates a sequence of floating-point numbers using a generator.
    
    Parameters:
        length (int): Length of the sequence

    Yields:
        float: a floating-point number input by the user
    """
    for _ in range(length):
        while True:  # Keep asking for valid input until it's correct
            try:
                value = float(input("Enter a floating-point number: "))  # Convert input to float
                yield value  # Return the value to the generator
                break  # Exit the loop if input is valid
            except ValueError:
                print("Invalid input! Please enter a valid floating-point number.")
