def common_items(a, b):
    result = []
    for item in a:
        if item in b and item not in result:
            result.append(item)
    return result


def has_pair_with_sum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return True
    return False


def word_frequencies(text):
    words = text.split()
    freq = {}
    for w in words:
        if w not in freq:
            freq[w] = words.count(w)
    return freq


def build_report(rows):
    report = ""
    for name, value in rows:
        report = report + f"{name}: {value}\n"
    return report


if __name__ == "__main__":
    import random

    n = 8000
    a = [random.randrange(n) for _ in range(n)]
    b = [random.randrange(n) for _ in range(n)]
    common_items(a, b)
    has_pair_with_sum(a, -1)
    word_frequencies(" ".join(f"w{x % 500}" for x in a))
    build_report((f"row{i}", i) for i in range(n))
