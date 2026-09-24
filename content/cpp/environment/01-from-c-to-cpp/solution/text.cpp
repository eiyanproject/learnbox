#include "text.h"

#include <algorithm>
#include <cctype>
#include <sstream>

std::string join(const std::vector<std::string>& parts, const std::string& sep) {
    std::string out;
    for (size_t i = 0; i < parts.size(); ++i) {
        if (i > 0) {
            out += sep;
        }
        out += parts[i];
    }
    return out;
}

int word_count(const std::string& text) {
    std::istringstream in(text);
    std::string word;
    int count = 0;
    while (in >> word) {
        ++count;
    }
    return count;
}

std::string to_upper(std::string text) {
    // Taken by value, so this is already a copy the caller does not share.
    std::transform(text.begin(), text.end(), text.begin(),
                   [](unsigned char c) { return static_cast<char>(std::toupper(c)); });
    return text;
}

std::string longest(const std::vector<std::string>& parts) {
    std::string best;
    for (const auto& part : parts) {
        if (part.size() > best.size()) {
            best = part;
        }
    }
    return best;
}
