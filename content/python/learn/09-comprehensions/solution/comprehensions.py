def evens_squared(numbers):
    return [n * n for n in numbers if n % 2 == 0]


def lengths(words):
    return {word: len(word) for word in words}


def flatten(grid):
    return [x for row in grid for x in row]


def multiplication_table(n):
    return [[(i + 1) * (j + 1) for j in range(n)] for i in range(n)]
