#include "lru.h"

LruCache::LruCache(std::size_t capacity) : capacity_(capacity) {}

std::optional<int> LruCache::get(const std::string& key) {
    auto found = index_.find(key);
    if (found == index_.end()) {
        return std::nullopt;
    }
    order_.splice(order_.begin(), order_, found->second);
    return found->second->second;
}

void LruCache::put(const std::string& key, int value) {
    if (capacity_ == 0) {
        return;
    }
    auto found = index_.find(key);
    if (found != index_.end()) {
        found->second->second = value;
        order_.splice(order_.begin(), order_, found->second);
        return;
    }
    order_.emplace_front(key, value);
    index_[key] = order_.begin();
    if (order_.size() > capacity_) {
        index_.erase(order_.back().first);
        order_.pop_back();
    }
}

bool LruCache::contains(const std::string& key) const {
    return index_.count(key) > 0;
}

std::size_t LruCache::size() const {
    return order_.size();
}

std::vector<std::string> LruCache::keys() const {
    std::vector<std::string> out;
    for (const auto& entry : order_) {
        out.push_back(entry.first);
    }
    return out;
}
