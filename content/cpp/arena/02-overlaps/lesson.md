---
title: "Round 2: Overlaps"
summary: A calendar full of overlapping bookings. Merge them into the stretches that are actually busy.
order: 2
files: [intervals.cpp, intervals.h]
run: g++ -std=c++20 -Wall -c intervals.cpp
challenge:
  minutes: 18
  xp: 200
  requires:
    xp: 300
---

The meeting room's bookings overlap, repeat and arrive in no order. The
display by the door needs the stretches when the room is busy.

## The task

In `intervals.cpp`, define the function declared in `intervals.h`:

```cpp
using Interval = std::pair<int, int>;   // {start, end}, start <= end

std::vector<Interval> merge_intervals(std::vector<Interval> intervals);
```

Return the intervals merged so that none of them overlap, sorted by start.

- Two intervals merge when they overlap **or touch**: `{1, 3}` and `{3, 5}`
  become `{1, 5}`.
- Intervals that only come close stay apart: `{1, 2}` and `{3, 4}` are two
  intervals.
- An interval inside another disappears into it.
- The input can be in any order, and can be empty.

```text
{{1, 3}, {2, 6}, {8, 10}}          ->  {{1, 6}, {8, 10}}
{{5, 7}, {1, 3}, {3, 5}}           ->  {{1, 7}}
{{1, 10}, {2, 3}, {4, 5}}          ->  {{1, 10}}
```
