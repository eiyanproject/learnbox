#ifndef INTERVALS_H
#define INTERVALS_H

#include <utility>
#include <vector>

using Interval = std::pair<int, int>;  // {start, end}, start <= end

std::vector<Interval> merge_intervals(std::vector<Interval> intervals);

#endif
