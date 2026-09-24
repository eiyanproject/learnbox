#ifndef ALGO_H
#define ALGO_H

#include <stdexcept>
#include <vector>

template <typename T>
T largest(const std::vector<T>& values) {
    if (values.empty()) {
        // There is no largest element of nothing; inventing one would be
        // worse than refusing.
        throw std::invalid_argument("largest of an empty vector");
    }
    T best = values.front();
    for (const auto& v : values) {
        if (best < v) {
            best = v;
        }
    }
    return best;
}

template <typename T, typename Pred>
int count_if_matching(const std::vector<T>& values, Pred pred) {
    int count = 0;
    for (const auto& v : values) {
        if (pred(v)) {
            count++;
        }
    }
    return count;
}

template <typename T, typename F>
auto transform_all(const std::vector<T>& values, F f) {
    std::vector<decltype(f(values.front()))> out;
    out.reserve(values.size());
    for (const auto& v : values) {
        out.push_back(f(v));
    }
    return out;
}

template <typename T>
T sum_all(const std::vector<T>& values, T initial) {
    T total = initial;
    for (const auto& v : values) {
        total = total + v;
    }
    return total;
}

#endif
