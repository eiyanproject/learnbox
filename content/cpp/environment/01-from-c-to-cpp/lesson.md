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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **standard library** | the classes and functions every C++ compiler provides, in namespace `std` |
| **namespace** | a named group of names; `std::` means "from the standard library" |
| **object** | a value of a class type |
| **destructor** | a function that runs automatically when an object goes out of scope |
| **scope** | the `{ }` block a name lives in |
| **RAII** | resource acquisition is initialisation: an object owns a resource and releases it in its destructor |
| **resource** | anything that must be released: memory, a file, a lock |
| **exception** | an error thrown and caught elsewhere; destructors still run |
| **`new`** / **`delete`** | manual allocation and release; rare in modern C++ |
| **reference** | an alias for an existing object; never null, never repointed |
| **`const&`** | a reference that cannot modify: no copy, no change |
| **container** | a class holding many values, such as `std::vector` |
| **algorithm** | a standard function working on a range, such as `std::sort` |
| **iterator** | an object marking a position in a container |
| **range** | a pair of iterators: begin and end |
| **contiguous** | elements side by side in memory |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `g++ -std=c++20 -Wall text.cpp -o text && ./text` | compiles and runs C++ |

### C++ names

| Name | What it does |
|---|---|
| `#include <string>`, `<vector>`, `<algorithm>`, `<iostream>` | standard headers |
| `std::string a = "hello"; a += " world";` | a string that grows itself |
| `a.size()` | its length |
| `a == "hello world"` | compares contents (with `char*`, `==` compares addresses) |
| `std::vector<int> v = {3, 1, 2};` | a growable array |
| `std::sort(v.begin(), v.end())` | sorts a range |
| `std::find(v.begin(), v.end(), 2)` | returns an iterator to the match, or `end()` |
| `auto` | lets the compiler work out the type |
| `std::cout << x << "\n"` | prints; a `bool` prints as `1` or `0` |
| `it - v.begin()` | the index an iterator points at |

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

The string and container claims above, in a program you can compile:

```cpp
#include <algorithm>
#include <iostream>
#include <string>
#include <vector>

int main() {
    std::string a = "hello";
    a += " world";
    std::cout << a.size() << " " << (a == "hello world") << "\n";

    const char* p = "hi";
    char q[] = "hi";
    std::cout << (p == q) << "\n";      // same text, different addresses

    std::vector<int> v = {3, 1, 2};
    std::sort(v.begin(), v.end());
    auto it = std::find(v.begin(), v.end(), 2);
    std::cout << v[0] << v[1] << v[2] << ", 2 is at index " << (it - v.begin()) << "\n";
}
```

```output
11 1
0
123, 2 is at index 1
```

`std::cout` prints a `bool` as `1` or `0`.

## Your turn

In `text.h` and `text.cpp`:

- `std::string join(const std::vector<std::string>& parts, const std::string& sep)`
- `int word_count(const std::string& text)` — whitespace-separated
- `std::string to_upper(std::string text)` — a new string
- `std::string longest(const std::vector<std::string>& parts)` — the first
  longest, or `""`
