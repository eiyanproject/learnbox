import bisect
import heapq
from collections import Counter, defaultdict, deque


def top_words(text, n):
    return Counter(text.lower().split()).most_common(n)


def index_by_tag(items):
    index = defaultdict(list)
    for name, tags in items:
        for tag in tags:
            index[tag].append(name)
    return dict(index)


def moving_average(values, window):
    recent = deque(maxlen=window)
    for v in values:
        recent.append(v)
        if len(recent) == window:
            yield sum(recent) / window


def k_smallest(items, k):
    return heapq.nsmallest(k, items)


def grade_for(score):
    return "FDCBA"[bisect.bisect([60, 70, 80, 90], score)]
