def winner(votes):
    counts = {}
    for vote in votes:
        name = vote.strip().capitalize()
        counts[name] = counts.get(name, 0) + 1
    if not counts:
        return None
    best = max(counts.values())
    return min(name for name, n in counts.items() if n == best)
