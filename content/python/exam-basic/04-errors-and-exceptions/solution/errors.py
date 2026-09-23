class AgeError(ValueError):
    pass


def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return "undefined"


def parse_ints(items):
    result = []
    for item in items:
        try:
            result.append(int(item))
        except (ValueError, TypeError):
            continue
    return result


def trace_order(should_raise):
    steps = []
    try:
        steps.append("try")
        if should_raise:
            raise ValueError("boom")
    except ValueError:
        steps.append("except")
    else:
        steps.append("else")
    finally:
        steps.append("finally")
    return steps


def validate_age(age):
    if age < 0:
        raise AgeError("age must not be negative")
    return age
