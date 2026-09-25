#ifndef PARSE_H
#define PARSE_H

#include <optional>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

inline std::optional<int> parse_int(std::string_view text) {
    if (text.empty()) {
        return std::nullopt;
    }
    std::size_t i = 0;
    bool negative = false;
    if (text[0] == '-') {
        negative = true;
        i = 1;
        if (text.size() == 1) {
            return std::nullopt; // "-" alone is not a number
        }
    }
    long value = 0;
    for (; i < text.size(); ++i) {
        if (text[i] < '0' || text[i] > '9') {
            return std::nullopt;
        }
        value = value * 10 + (text[i] - '0');
    }
    return static_cast<int>(negative ? -value : value);
}

inline int divide(int a, int b) {
    // The caller cannot sensibly continue with a zero divisor, so this is an
    // exception rather than an empty optional.
    if (b == 0) {
        throw std::domain_error("division by zero");
    }
    return a / b;
}

inline std::vector<int> parse_all(const std::vector<std::string>& items, int* failed) {
    std::vector<int> out;
    int bad = 0;
    for (const auto& item : items) {
        if (auto value = parse_int(item)) {
            out.push_back(*value);
        } else {
            ++bad; // one bad entry must not lose the rest
        }
    }
    if (failed != nullptr) {
        *failed = bad;
    }
    return out;
}

inline int parse_or(std::string_view text, int fallback) {
    return parse_int(text).value_or(fallback);
}

#endif
