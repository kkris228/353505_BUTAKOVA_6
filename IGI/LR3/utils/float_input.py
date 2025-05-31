def get_float(prompt: str) -> float:
    """
    Prompts user for a float with validation.
    """
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Please enter a valid number.")