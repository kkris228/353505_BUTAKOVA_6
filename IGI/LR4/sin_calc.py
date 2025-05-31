import math
import numpy as np
import matplotlib.pyplot as plt
from statistics import mean, median, mode, variance, stdev


class SinSeriesAnalyzer:
    """
    Class to analyze sin(x) via Taylor series expansion and compare with math.sin.
    Computes statistics and plots graphs.
    """

    def __init__(self, x_start, x_end, x_step, max_terms=10, eps=1e-6):
        """
        Initialize parameters.

        :param x_start: start of x range
        :param x_end: end of x range
        :param x_step: step for x
        :param max_terms: max number of terms in Taylor series
        :param eps: accuracy threshold to stop adding terms
        """
        self.x_values = np.arange(x_start, x_end + x_step, x_step)
        self.max_terms = max_terms
        self.eps = eps
        self.results = []  # will store tuples (x, n, F(x), mathF, eps)

    def taylor_sin(self, x):
        """
        Compute sin(x) using Taylor series expansion until max_terms or eps reached.

        Returns sum, number of terms used.
        """
        s = 0.0
        for n in range(self.max_terms):
            term = ((-1) ** n) * (x ** (2 * n + 1)) / math.factorial(2 * n + 1)
            s += term
            if abs(term) < self.eps:
                return s, n + 1
        return s, self.max_terms

    def analyze(self):
        """Compute series and math.sin values and store results."""
        for x in self.x_values:
            f_x, n_terms = self.taylor_sin(x)
            math_fx = math.sin(x)
            error = abs(f_x - math_fx)
            self.results.append((x, n_terms, f_x, math_fx, error))

    def print_table(self):
        """Print results in table format."""
        print(f"{'x':>8} | {'n':>3} | {'F(x)':>12} | {'Math F(x)':>12} | {'eps':>10}")
        print("-" * 55)
        for x, n, fx, mfx, e in self.results:
            print(f"{x:8.4f} | {n:3} | {fx:12.8f} | {mfx:12.8f} | {e:10.2e}")

    def compute_statistics(self):
        """Compute additional statistics on F(x) values."""
        fx_values = [r[2] for r in self.results]

        avg = mean(fx_values)
        med = median(fx_values)
        try:
            md = mode(fx_values)
        except:
            md = 'No unique mode'
        var = variance(fx_values)
        sd = stdev(fx_values)

        print("\nStatistics for F(x):")
        print(f"Mean: {avg:.6f}")
        print(f"Median: {med:.6f}")
        print(f"Mode: {md}")
        print(f"Variance: {var:.6f}")
        print(f"Standard deviation: {sd:.6f}")

        return avg, med, md, var, sd

    def plot(self, filename='sin_series_plot.png'):
        """Plot series and math.sin on same graph with legends and annotations."""
        x_vals = [r[0] for r in self.results]
        fx_vals = [r[2] for r in self.results]
        math_vals = [r[3] for r in self.results]

        plt.figure(figsize=(10, 6))
        plt.plot(x_vals, fx_vals, label='Taylor Series sin(x)', color='blue')
        plt.plot(x_vals, math_vals, label='math.sin(x)', color='red', linestyle='--')

        plt.title('Sin(x) Approximation by Taylor Series vs math.sin')
        plt.xlabel('x')
        plt.ylabel('Function Value')
        plt.grid(True)
        plt.legend()

        errors = [abs(a - b) for a, b in zip(fx_vals, math_vals)]
        max_err = max(errors)
        max_err_index = errors.index(max_err)
        max_err_x = x_vals[max_err_index]
        max_err_y = fx_vals[max_err_index]

        plt.annotate(f'Max error = {max_err:.2e}',
                     xy=(max_err_x, max_err_y),
                     xytext=(max_err_x, max_err_y + 0.5),
                     arrowprops=dict(facecolor='black', shrink=0.05),
                     fontsize=10)

        plt.axhline(0, color='black', linewidth=0.5)
        plt.axvline(0, color='black', linewidth=0.5)

        plt.savefig(filename)
        print(f"\nPlot saved to {filename}")
        plt.show()
