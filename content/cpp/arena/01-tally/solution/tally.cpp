#include "tally.h"

#include <algorithm>
#include <map>

std::string most_common(const std::vector<std::string>& words) {
    std::map<std::string, int> counts;
    for (const auto& word : words) {
        ++counts[word];
    }
    std::string best;
    int most = 0;
    // A map iterates in key order, so the first to reach the top count is
    // also the first alphabetically.
    for (const auto& [word, count] : counts) {
        if (count > most) {
            most = count;
            best = word;
        }
    }
    return best;
}

std::vector<int> unique_sorted(const std::vector<int>& values) {
    std::vector<int> out = values;
    std::sort(out.begin(), out.end());
    out.erase(std::unique(out.begin(), out.end()), out.end());
    return out;
}
