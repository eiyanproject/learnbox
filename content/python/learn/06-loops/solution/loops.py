def sum_to(n):
    total = 0
    for i in range(1, n + 1):
        total += i
    return total


def fizzbuzz(n):
    result = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            result.append("FizzBuzz")
        elif i % 3 == 0:
            result.append("Fizz")
        elif i % 5 == 0:
            result.append("Buzz")
        else:
            result.append(str(i))
    return result


def collatz_steps(n):
    steps = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    return steps


def first_repeated(words):
    seen = set()
    for word in words:
        if word in seen:
            return word
        seen.add(word)
    return None
