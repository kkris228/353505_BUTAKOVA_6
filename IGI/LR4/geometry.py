import math
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt


class GeometricFigure(ABC):
    """Abstract base class for geometric figures."""

    @abstractmethod
    def area(self):
        """Calculate area of the figure."""
        pass


class ColorFigure:
    """Class to hold color property for figures."""

    def __init__(self, color):
        self._color = None
        self.color = color  # setter called

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value


class Rhombus(GeometricFigure):
    """Rhombus figure with side 'a', acute angle 'R' in degrees and color."""

    figure_name = "Rhombus"  # class field

    def __init__(self, a, R_deg, color):
        self.a = a
        self.R_deg = R_deg
        self.color_figure = ColorFigure(color)

    @classmethod
    def get_name(cls):
        return cls.figure_name

    def area(self):
        """Calculate area S = a^2 * sin(R)."""
        R_rad = math.radians(self.R_deg)
        return self.a ** 2 * math.sin(R_rad)

    def parameters_str(self):
        """Return formatted string with parameters, color and area."""
        return ("Figure: {name}\n"
                "Side a: {a}\n"
                "Angle R: {R} degrees\n"
                "Color: {color}\n"
                "Area: {area:.4f}").format(
            name=self.get_name(),
            a=self.a,
            R=self.R_deg,
            color=self.color_figure.color,
            area=self.area())

    def plot(self, text_label, filename="rhombus.png"):
        """Draw rhombus, fill color, add text label, save and show."""
        R_rad = math.radians(self.R_deg)
        a = self.a

        # Coordinates of rhombus vertices starting at (0,0)
        x0, y0 = 0, 0
        x1, y1 = a, 0
        x2, y2 = a + a * math.cos(R_rad), a * math.sin(R_rad)
        x3, y3 = a * math.cos(R_rad), a * math.sin(R_rad)

        xs = [x0, x1, x2, x3, x0]
        ys = [y0, y1, y2, y3, y0]

        plt.figure()
        plt.fill(xs, ys, self.color_figure.color, alpha=0.5)
        plt.plot(xs, ys, color='black')
        plt.text(sum(xs)/4, sum(ys)/4, text_label, fontsize=12, ha='center', va='center')
        plt.axis('equal')
        plt.title(f"{self.get_name()} ({self.color_figure.color})")
        plt.grid(True)

        plt.savefig(filename)
        print(f"Rhombus image saved as '{filename}'")
        plt.show()
