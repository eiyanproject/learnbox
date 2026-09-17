def grade(score):
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    return "F"


def is_leap_year(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def ticket_price(age, weekend):
    if age < 3 or age >= 65:
        return 0
    if age <= 12:
        return 8
    return 18 if weekend else 15


def describe_number(n):
    if n == 0:
        return "zero"
    sign = "positive" if n > 0 else "negative"
    parity = "even" if n % 2 == 0 else "odd"
    return f"{sign} {parity}"
