#ifndef RANGES_H
#define RANGES_H

#include <algorithm>
#include <cstddef>
#include <iterator>
#include <ranges>
#include <vector>

template <typename It>
auto sum_range(It first, It last) {
    // The range is half-open: last is one past the end, so an empty range is
    // first == last and needs no special case.
    typename std::iterator_traits<It>::value_type total{};
    for (; first != last; ++first) {
        total += *first;
    }
    return total;
}

inline void remove_all(std::vector<int>& values, int value) {
    // std::remove only shuffles survivors forward and returns the new logical
    // end; erase is what actually shortens the vector.
    values.erase(std::remove(values.begin(), values.end(), value), values.end());
}

inline std::vector<int> evens_doubled(const std::vector<int>& values) {
    auto view = values
        | std::views::filter([](int n) { return n % 2 == 0; })
        | std::views::transform([](int n) { return n * 2; });
    std::vector<int> out;
    for (int n : view) {
        out.push_back(n);
    }
    return out;
}

inline std::size_t count_between(const std::vector<int>& values, int lo, int hi) {
    return static_cast<std::size_t>(
        std::ranges::count_if(values, [lo, hi](int n) { return n >= lo && n <= hi; }));
}

#endif
