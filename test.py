# Integer division by zero raises an error
try:
    print(1 // 0)
except ZeroDivisionError as e:
    print(f"Integer division error: {e}")

# Float division by zero returns infinity
print(1.0 / 0)  # Output: inf
