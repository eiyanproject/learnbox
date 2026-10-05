#ifndef LRU_H
#define LRU_H

#include <cstddef>
#include <list>
#include <optional>
#include <string>
#include <unordered_map>
#include <vector>

class LruCache {
public:
    explicit LruCache(std::size_t capacity);

    std::optional<int> get(const std::string& key);
    void put(const std::string& key, int value);
    bool contains(const std::string& key) const;
    std::size_t size() const;
    std::vector<std::string> keys() const;

private:
    // Add the members you need.
};

#endif
