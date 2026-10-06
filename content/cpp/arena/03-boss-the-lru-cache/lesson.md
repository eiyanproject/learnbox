---
title: "Boss: The LRU cache"
summary: A cache with a size limit that throws out whatever was used longest ago. Design the data structure yourself.
order: 4
files: [lru.cpp, lru.h]
run: g++ -std=c++20 -Wall -c lru.cpp
challenge:
  boss: true
  minutes: 30
  xp: 500
  requires:
    xp: 550
---

The lookup service is slow and memory is short. It needs a cache that holds
a fixed number of entries and, when it is full, forgets the one nobody has
touched for longest.

## The task

`lru.h` declares the class `LruCache` with its public interface and an empty
`private` section. Add the data members you need to the header, and define
the member functions in `lru.cpp`. Do not change the public interface.

```cpp
class LruCache {
public:
    explicit LruCache(std::size_t capacity);

    std::optional<int> get(const std::string& key);
    void put(const std::string& key, int value);
    bool contains(const std::string& key) const;
    std::size_t size() const;
    std::vector<std::string> keys() const;
};
```

- `put` stores a value under a key, or replaces the value if the key is
  already there. Either way that key becomes the **most recently used**. If
  the cache now holds more than `capacity` entries, the **least recently
  used** one is removed.
- `get` returns the value, or `std::nullopt` if the key is not there. A
  successful `get` makes the key the most recently used. A miss changes
  nothing.
- `contains` says whether the key is there **without** counting as a use.
- `size` is the number of entries.
- `keys` lists the keys from most recently used to least.
- A cache with capacity `0` stores nothing.

```cpp
LruCache cache(2);
cache.put("a", 1);
cache.put("b", 2);
cache.get("a");        // 1, and "a" is now the most recent
cache.put("c", 3);     // over capacity: "b" is the least recent, and goes
cache.keys();          // {"c", "a"}
cache.get("b");        // std::nullopt
```

Any design that behaves like this passes. The classic one keeps a
`std::list` in use order and a `std::unordered_map` from key to list
iterator, which makes every operation constant time.
