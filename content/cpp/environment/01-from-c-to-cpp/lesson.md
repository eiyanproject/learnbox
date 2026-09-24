---
title: What C++ adds, and what it keeps
summary: RAII and the standard library instead of manual memory, references instead of pointers where you can, and why std::string is not char*.
order: 1
files: [text.cpp, text.h]
run: g++ -std=c++20 -Wall text.cpp -o text && ./text
hints:
  - "`join` takes a `const std::vector<std::string>&` - by reference so nothing is copied, const so it cannot be modified."
  - "`word_count` can use a std::istringstream and `>>`, which splits on whitespace for you."
  - "`to_upper` should return a NEW string rather than modifying its argument; take it by value and transform in place, or copy first."
  - "`longest` returns the first longest when there is a tie, and an empty string for an empty vector."
---

C++ compiles the same way C does and adds two things that change how you write
it: the standard library, and destructors that run automatically.

## RAII

A C++ object's destructor runs when it goes out of scope. That single rule
removes most manual cleanup:

```cpp
{
    std::vector<int> values(1000);   // allocates
    std::string name = "ada";        // allocates
}                                     // both freed here, including on an exception
```

No `free`, no `delete`, no leak on the error path. This is **RAII** —
resource acquisition is initialisation — and it is why modern C++ rarely
contains `new` or `delete` at all. A resource is owned by an object, and the
object's lifetime is the resource's lifetime.

## std::string is not char*

```cpp
std::string a = "hello";
a += " world";          // grows itself
a.size();               // knows its length
a == "hello world";     // compares contents
```

A `char*` knows nothing: not its length, not who owns it, not whether it is
still valid. Comparing two with `==` compares addresses. `std::string` fixes
all of that and costs an allocation, which is almost never the thing making
your program slow.

## References

```cpp
void print(const std::string& s);     // no copy, cannot modify
void modify(std::string& s);          // no copy, can modify
void take(std::string s);             // a copy
```

A reference is an alias, not an address you can reseat: it cannot be null and
cannot be repointed. Pass big things by `const&` and you get C's efficiency
without C's uncertainty about ownership.

## Containers and algorithms

```cpp
std::vector<int> v = {3, 1, 2};
std::sort(v.begin(), v.end());
auto it = std::find(v.begin(), v.end(), 2);
```

`std::vector` is the default container — contiguous, growable, cache-friendly.
The algorithms in `<algorithm>` work on any range, so the same `sort` serves
every container.

## Your turn

In `text.h` and `text.cpp`:

- `std::string join(const std::vector<std::string>& parts, const std::string& sep)`
- `int word_count(const std::string& text)` — whitespace-separated
- `std::string to_upper(std::string text)` — a new string
- `std::string longest(const std::vector<std::string>& parts)` — the first
  longest, or `""`
