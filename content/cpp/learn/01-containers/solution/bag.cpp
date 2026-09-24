#include "bag.h"

#include <algorithm>

std::vector<int> evens_in(const std::vector<int>& values) {
    std::vector<int> out;
    for (const auto& v : values) {
        if (v % 2 == 0) {
            out.push_back(v);
        }
    }
    return out;
}

int sum(const std::vector<int>& values) {
    int total = 0;
    for (const auto& v : values) {
        total += v;
    }
    return total;
}

std::vector<int> sorted_copy(std::vector<int> values) {
    // Taken by value: this is already the caller's copy, so sorting it here
    // cannot touch theirs.
    std::sort(values.begin(), values.end());
    return values;
}

int count_longer_than(const std::vector<std::string>& words, std::size_t n) {
    int count = 0;
    for (const auto& word : words) {
        if (word.size() > n) {
            count++;
        }
    }
    return count;
}

bool contains(const std::vector<int>& values, int target) {
    return std::find(values.begin(), values.end(), target) != values.end();
}
