"""
This module demonstrates a simple circle class and a function to calculate the area of a circle.
(Module docstrings are optional but good practice in python)
"""
from enum import Enum
import math
import unittest

# Module-level global
RAD = 5


def calculate_area(radius: float) -> float:
    """Function to calculate the area of a circle."""
    return math.pi * radius * radius


# Multiline comments in python feels like a hack
"""
Above we have the demonstration of a function to calculate the area of a circle.
Below we have the demonstration of a class to calculate the area of a circle.
"""


# Enum for shape types
class ShapeType(Enum):
    CIRCLE = "Circle"
    UNKNOWN = "Unknown"


class Shape:
    """Base class for a shape."""

    def __init__(self, shape_type: ShapeType):
        self.shape_type = shape_type

    def area(self) -> float:
        """Returns the area of the shape."""
        pass


class Circle(Shape):
    """Circle class inherits from Shape."""

    def __init__(self, radius: float):
        super().__init__(ShapeType.CIRCLE)
        self.radius = radius

    def area(self) -> float:
        """Overridden method to calculate the area of the circle."""
        return math.pi * self.radius * self.radius


c = Circle(RAD)

if __name__ == "__main__":
    # To run the program functionality
    print(f"Area of a circle with radius {RAD} using function: {calculate_area(RAD)}")
    print(f"Area of a {c.shape_type.value} with radius {RAD} using class: {c.area()}")

    # Uncomment the next line if you want to run the unit tests
    # run_tests()


# Unit Tests!
class TestShapesFunctions(unittest.TestCase):
    def test_calculate_area(self):
        expected_area = 78.53981633974483
        self.assertAlmostEqual(calculate_area(RAD), expected_area)

    def test_circle_area(self):
        c = Circle(RAD)
        expected_area = 78.53981633974483
        self.assertAlmostEqual(c.area(), expected_area)

    def test_circle_type(self):
        c = Circle(RAD)
        self.assertEqual(c.shape_type, ShapeType.CIRCLE)