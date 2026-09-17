from collections import Counter


def common_items(a, b):
    in_b = set(b)
    seen = set()
    result = []
    for item in a:
        if item in in_b and item not in seen:
            seen.add(item)
            result.append(item)
    return result


def has_pair_with_sum(nums, target):
    seen = set()
    for x in nums:
        if target - x in seen:
            return True
        seen.add(x)
    return False


def word_frequencies(text):
    return dict(Counter(text.split()))


def build_report(rows):
    return "".join(f"{name}: {value}\n" for name, value in rows)


if __name__ == "__main__":
    import random

    n = 8000
    a = [random.randrange(n) for _ in range(n)]
    b = [random.randrange(n) for _ in range(n)]
    common_items(a, b)
    has_pair_with_sum(a, -1)
    word_frequencies(" ".join(f"w{x % 500}" for x in a))
    build_report((f"row{i}", i) for i in range(n))
