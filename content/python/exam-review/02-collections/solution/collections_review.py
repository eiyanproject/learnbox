def word_frequency(text):
    counts = {}
    for word in text.lower().split():
        counts[word] = counts.get(word, 0) + 1
    return counts


def group_by_length(words):
    groups = {}
    for word in words:
        groups.setdefault(len(word), []).append(word)
    for bucket in groups.values():
        bucket.sort()
    return groups


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def common_items(a, b):
    return sorted(set(a) & set(b))
