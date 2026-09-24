---
title: vector, string and the range-for
summary: The container you should reach for by default, what auto really means, and iterating without an index.
order: 1
files: [bag.cpp, bag.h]
run: g++ -std=c++20 -Wall bag.cpp -o bag && ./bag
hints:
  - "`push_back` appends; `size()` is the count; `empty()` is clearer than `size() == 0` and the tests do not care which you use."
  - "Use a range-for where you do not need the index: `for (const auto& item : items)` - const auto& avoids copying each element."
  - "`std::sort(v.begin(), v.end())` sorts in place. Include <algorithm> for it."
  - "`count_longer_than` compares `s.size() > n` - size() returns size_t, so take n as size_t or cast, or the compiler warns about a signed/unsigned comparison."
---

`std::vector` is the default container in C++. Contiguous like a C array,
growable like a list, and it knows its own length.

```cpp
std::vector<int> v;
v.push_back(3);
v.size();            // 1
v[0];                // no bounds check
v.at(0);             // bounds checked, throws std::out_of_range
```

`operator[]` does not check; `at()` does and costs a comparison. Use `at` while
learning and in anything reading external input.

## Range-for

```cpp
for (const auto& item : items) { ... }   // read only, no copy
for (auto& item : items) { item *= 2; }  // modify in place
for (auto item : items) { ... }          // a copy of each element
```

The `&` matters. Without it every element is copied — invisible for `int`,
expensive for `std::string`, and a real bug if you meant to modify.

## auto

`auto` asks the compiler to work out the type from the initialiser. It is not
dynamic typing; the type is fixed at compile time and unchangeable.

```cpp
auto n = 5;                          // int
auto name = std::string{"ada"};      // std::string
auto it = v.begin();                 // some iterator type you need not name
```

The third is the real motivation: iterator types are long and saying them adds
nothing.

## The containers worth knowing first

| | |
|---|---|
| `std::vector<T>` | the default: contiguous, growable |
| `std::string` | a vector of characters with text operations |
| `std::map<K,V>` | sorted key-value, O(log n) |
| `std::unordered_map<K,V>` | hashed key-value, O(1) average |
| `std::array<T,N>` | fixed size, knows its length, no allocation |

## Algorithms

```cpp
#include <algorithm>
std::sort(v.begin(), v.end());
auto it = std::find(v.begin(), v.end(), 42);
if (it != v.end()) { /* found */ }
```

Algorithms take iterator **ranges**, not containers, which is why the same
`sort` works on a vector, an array, or part of either. A search returns `end()`
to mean "not found" — comparing against `end()` is the idiom.

## Your turn

In `bag.h` and `bag.cpp`:

- `std::vector<int> evens_in(const std::vector<int>& values)`
- `int sum(const std::vector<int>& values)`
- `std::vector<int> sorted_copy(std::vector<int> values)` — sorted, leaving
  the caller's vector alone
- `int count_longer_than(const std::vector<std::string>& words, std::size_t n)`
- `bool contains(const std::vector<int>& values, int target)`
