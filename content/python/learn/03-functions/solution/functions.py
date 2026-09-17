def square(n):
    return n * n


def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"


def bmi(weight_kg, height_m):
    return round(weight_kg / height_m**2, 1)


def split_bill(total, people):
    share = round(total / people, 2)
    return share, round(total - share * people, 2)
