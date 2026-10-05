#include "intervals.h"

#include <algorithm>

std::vector<Interval> merge_intervals(std::vector<Interval> intervals) {
    std::sort(intervals.begin(), intervals.end());
    std::vector<Interval> out;
    for (const auto& [start, end] : intervals) {
        if (!out.empty() && start <= out.back().second) {
            out.back().second = std::max(out.back().second, end);
        } else {
            out.emplace_back(start, end);
        }
    }
    return out;
}
