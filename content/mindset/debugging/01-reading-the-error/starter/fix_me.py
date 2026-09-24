def average(values):
    """ZeroDivisionError: division by zero"""
    return sum(values) / len(values)


def get_first_word(text):
    """IndexError: list index out of range"""
    return text.split()[0]


def total_price(items):
    """TypeError: can't multiply sequence by non-int of type 'float'"""
    return sum(quantity * price for quantity, price in items)


def find_user(users, name):
    """AttributeError: 'NoneType' object has no attribute 'upper'"""
    for user in users:
        if user == name:
            user
