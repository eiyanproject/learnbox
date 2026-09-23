def arithmetic_facts(a, b):
    return {
        "quotient": a / b,
        "floor": a // b,
        "remainder": a % b,
        "power": a**b,
    }


def slice_word(word):
    return word[:3], word[-3:], word[::-1], word[::2]


def replace_slice(values):
    values[1:4] = [0, 0]
    return values


def build_matrix(rows, cols):
    return [[r * cols + c for c in range(cols)] for r in range(rows)]
