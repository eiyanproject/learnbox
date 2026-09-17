def word_counts(text):
    counts = {}
    for raw in text.split():
        word = raw.lower().strip(".,!?;:")
        if word:
            counts[word] = counts.get(word, 0) + 1
    return counts


def invert(d):
    return {value: key for key, value in d.items()}


def group_by_first_letter(words):
    groups = {}
    for word in words:
        groups.setdefault(word[0].lower(), []).append(word)
    return groups


def common_friends(a, b):
    return sorted(set(a) & set(b))
