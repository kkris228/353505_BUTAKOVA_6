"""
Task 1: sin(x) via Taylor series
Version: 1.0
Author: Butakova Kristina
Date: 16.04.2025
"""

import math
from utils.decorators import log_execution


@log_execution
def calculate_sin(x: float, eps: float, max_iter: int = 500) -> dict:
    """
    Calculates sin(x) using power series expansion.
    
    Parameters:
        x (float): The argument value.
        eps (float): Desired accuracy.
        max_iter (int): Maximum number of iterations.
    
    Returns:
        dict: x, Fx (approximate), MathFx (via math.sin), n (used terms)
    """
    term = x
    total = x
    n = 1

    while abs(term) >= eps and n < max_iter:
        term *= -x * x / ((2 * n) * (2 * n + 1))
        total += term
        n += 1

    return {
        "x": x,
        "Fx": total,
        "MathFx": math.sin(x),
        "n": n
    }