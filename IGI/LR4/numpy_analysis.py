import numpy as np


class NumpyAnalyzer:
    """
    Class to analyze integer matrix with NumPy:
    - array creation,
    - indexing,
    - universal functions,
    - statistical calculations,
    - custom calculations per task.
    """

    def __init__(self, n, m, low=-100, high=100):
        """
        Initialize matrix A[n,m] with random integers in [low, high).

        :param n: number of rows
        :param m: number of columns
        :param low: lower bound for random integers (inclusive)
        :param high: upper bound for random integers (exclusive)
        """
        self.n = n
        self.m = m
        self.A = np.random.randint(low, high, size=(n, m))
        print("Matrix A created:")
        print(self.A)

    def demonstrate_array_creation(self):
        print("\nDemonstrating array creation:")
        arr1 = np.array([1, 2, 3])
        print("Array from list:", arr1)

        arr2 = np.arange(5)
        print("arange(5):", arr2)

        arr3 = np.ones((2, 3))
        print("Ones 2x3 array:\n", arr3)

        arr4 = np.zeros((3, 2))
        print("Zeros 3x2 array:\n", arr4)

    def demonstrate_indexing(self):
        print("\nDemonstrating indexing and slicing:")
        print("Element A[0,0]:", self.A[0, 0])
        print("First row A[0, :]:", self.A[0, :])
        print("First column A[:, 0]:", self.A[:, 0])
        print("Slice A[1:3, 1:3]:\n", self.A[1:3, 1:3])

    def universal_functions(self):
        print("\nUniversal functions on A:")
        print("Absolute values:\n", np.abs(self.A))
        print("Square root of absolute values:\n", np.sqrt(np.abs(self.A)))

    def statistics(self):
        print("\nStatistical functions on A:")
        mean_val = np.mean(self.A)
        median_val = np.median(self.A)
        var_val = np.var(self.A)
        std_val = np.std(self.A)

        print(f"Mean: {mean_val:.4f}")
        print(f"Median: {median_val}")
        print(f"Variance: {var_val:.4f}")
        print(f"Standard deviation: {std_val:.4f}")

        return mean_val, median_val, var_val, std_val

    def correlation(self):
        print("\nCorrelation coefficient matrix of A:")
        if self.n > 1 and self.m > 1:
            # Compute correlation between rows
            corr = np.corrcoef(self.A)
            print(corr)
            return corr
        else:
            print("Matrix too small for correlation matrix")
            return None

    def sum_mod_neg_odd(self):
        print("\nSum of absolute values of negative odd elements:")
        cond = (self.A < 0) & (self.A % 2 != 0)
        neg_odd = self.A[cond]
        print("Negative odd elements:", neg_odd)
        sum_abs = np.sum(np.abs(neg_odd))
        print("Sum:", sum_abs)
        return sum_abs, neg_odd

    def std_dev_two_ways(self, values):
        print("\nStandard deviation of given values (rounded to 2 decimals):")

        std1 = np.std(values)
        print(f"Using numpy std: {std1:.2f}")

        # Manual calculation
        mean_val = np.mean(values)
        var_manual = np.mean((values - mean_val) ** 2)
        std_manual = np.sqrt(var_manual)
        print(f"Using manual formula: {std_manual:.2f}")

        return round(std1, 2), round(std_manual, 2)