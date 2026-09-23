def dedupe(values):
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def invert(mapping):
    inverted = {}
    for key, value in mapping.items():
        inverted.setdefault(value, []).append(key)
    for keys in inverted.values():
        keys.sort()
    return inverted


def rank_scores(scores):
    ordered = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
    return [(rank, name, score) for rank, (name, score) in enumerate(ordered, start=1)]


def set_report(a, b):
    a, b = set(a), set(b)
    return {
        "union": sorted(a | b),
        "common": sorted(a & b),
        "only_a": sorted(a - b),
        "symmetric": sorted(a ^ b),
    }
