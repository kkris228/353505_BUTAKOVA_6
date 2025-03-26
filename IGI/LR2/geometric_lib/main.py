import square
import circle

r = int(input("Circle radius(r): "))
a = int(input("Square side length(a): "))

circle_area = circle.area(r)
circle_perimeter = circle.perimeter(r)
square_area = square.area(a)
square_perimeter = square.perimeter(a)

print(f"square area: {square_area}")
print(f"square perimeter: {square_perimeter}")
print(f"circle area: {circle_area}")
print(f"circle perimeter: {circle_perimeter}")