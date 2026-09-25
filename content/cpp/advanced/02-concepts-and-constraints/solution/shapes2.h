#ifndef SHAPES2_H
#define SHAPES2_H

#include <concepts>
#include <string>
#include <vector>

template <typename T>
concept Numeric = std::integral<T> || std::floating_point<T>;

// A requires-expression only checks that the expression is well formed; nothing
// is evaluated and name() is never called here.
template <typename T>
concept Named = requires(const T& t) {
    { t.name() } -> std::convertible_to<std::string>;
};

template <Numeric T>
T sum(const std::vector<T>& values) {
    T total{};
    for (const T& value : values) {
        total += value;
    }
    return total;
}

template <Named T>
std::string label(const T& item) {
    return "[" + std::string(item.name()) + "]";
}

template <typename T>
std::string describe(const T& value) {
    // The branch not taken is discarded rather than compiled, so each branch
    // only has to be valid for the type that reaches it.
    if constexpr (Numeric<T>) {
        return "number " + std::to_string(value);
    } else if constexpr (Named<T>) {
        return "named " + std::string(value.name());
    } else {
        return "unknown";
    }
}

template <Numeric T>
T clamp_to(T value, T lo, T hi) {
    if (value < lo) {
        return lo;
    }
    if (value > hi) {
        return hi;
    }
    return value;
}

#endif
