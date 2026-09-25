#ifndef CT_H
#define CT_H

#include <array>
#include <cstddef>

constexpr int factorial(int n) {
    int result = 1;
    for (int i = 2; i <= n; ++i) {
        result *= i;
    }
    return result;
}

constexpr int fib(int n) {
    if (n < 2) {
        return n;
    }
    int a = 0;
    int b = 1;
    for (int i = 2; i <= n; ++i) {
        int next = a + b;
        a = b;
        b = next;
    }
    return b;
}

constexpr std::size_t length(const char* s) {
    std::size_t n = 0;
    while (s[n] != '\0') {
        ++n;
    }
    return n;
}

// consteval, not constexpr: passing a runtime value is a compile error, which
// is the whole reason to reach for it.
consteval int checked_percent(int n) {
    return (n < 0 || n > 100) ? throw "percent out of range" : n;
}

template <std::size_t N>
constexpr std::array<int, N> make_squares() {
    std::array<int, N> table{};
    for (std::size_t i = 0; i < N; ++i) {
        table[i] = static_cast<int>(i * i);
    }
    return table;
}

#endif
