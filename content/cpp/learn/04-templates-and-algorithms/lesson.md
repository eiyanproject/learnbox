---
title: Templates, lambdas and the algorithms
summary: Writing a function once for every type, passing behaviour as a value, and the standard algorithms that replace most loops.
order: 4
files: [algo.h]
run: g++ -std=c++20 -Wall -c algo.h -o /dev/null && echo "header compiles"
hints:
  - "Templates live entirely in the header: the compiler needs the body at every call site to instantiate it, so there is no .cpp for them."
  - "`largest` takes `const std::vector<T>&` and returns T. Throw std::invalid_argument for an empty vector rather than returning something made up."
  - "`count_if_matching` takes a predicate as a template parameter, so a lambda can be passed with no std::function and no allocation."
  - "`transform_all` builds a new vector by applying the function to each element - reserve the size first to avoid repeated reallocation."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **template** | code written once that the compiler generates per type used |
| **instantiate** | generate a template's version for one type |
| **type parameter** | `T` in `template <typename T>` |
| **type erasure** | hiding types behind one shared runtime form; templates do not do this |
| **call site** | where a function is called; needs the template's body |
| **lambda** | an anonymous function object: `[](int n) { ... }` |
| **capture** | variables a lambda takes from its scope |
| **capture list** | `[x]` copies, `[&x]` refers, `[=]` and `[&]` capture everything used |
| **function object** | an object you can call like a function |
| **dangling reference** | a reference to something already destroyed |
| **`std::function`** | holds any callable; costs an indirect call and maybe an allocation |
| **predicate** | a function returning true or false |
| **off-by-one** | a loop that runs one time too many or too few |
| **ranges** | C++20 algorithms that take the container directly |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `g++ -std=c++20 -Wall -c algo.h -o /dev/null` | checks that the header compiles; templates live in `algo.h` |
| `-o /dev/null` | throw the output away |

### C++ names

| Name | What it does |
|---|---|
| `template <typename T> T largest(const std::vector<T>&)` | a function template |
| `[threshold](int n) { return n > threshold; }` | a lambda capturing by value |
| `std::count_if(b, e, pred)` | counts matches |
| `std::transform(b, e, std::back_inserter(out), f)` | applies `f` to each, appending to `out` |
| `std::all_of`, `std::any_of`, `std::none_of` | test a predicate over a range |
| `std::accumulate(b, e, 0)` | sums, from `<numeric>` |
| `std::for_each(b, e, f)` | calls `f` on each element |
| `std::ranges::sort(v)` | the C++20 ranges version |
| `throw std::invalid_argument("...")` | the error for an empty input |

---

A template writes a function once and lets the compiler generate a version per
type actually used.

```cpp
template <typename T>
T largest(const std::vector<T>& values);
```

`largest<int>`, `largest<std::string>` and any other are generated on demand,
each fully type-checked. This is not type erasure — there is no shared runtime
representation and no cost for the abstraction.

## Templates live in headers

The compiler needs the **body** at each call site to instantiate it, so a
template defined in a `.cpp` cannot be used from anywhere else. Put templates
in the header; that is not a style choice, it is how instantiation works.

## Lambdas

A lambda is an anonymous function object, optionally capturing from its scope:

```cpp
auto is_even = [](int n) { return n % 2 == 0; };
int threshold = 5;
auto over = [threshold](int n) { return n > threshold; };   // by value
auto tally = [&count](int n) { count += n; };               // by reference
```

The `[...]` is the capture list: `[x]` copies, `[&x]` refers, `[=]` and `[&]`
capture everything used. Prefer naming what you capture — `[&]` makes it easy
to hold a reference to something that has already been destroyed.

Each lambda has its own unique type, which is why they are stored in `auto` or
passed as template parameters. Putting one in a `std::function` works and costs
an indirect call and possibly an allocation.

## Algorithms

```cpp
std::count_if(v.begin(), v.end(), is_even);
std::transform(v.begin(), v.end(), std::back_inserter(out), f);
std::all_of / any_of / none_of
std::accumulate(v.begin(), v.end(), 0);   // <numeric>
std::sort(v.begin(), v.end(), comparator);
```

Together, including what capturing by value means:

```cpp
#include <algorithm>
#include <iostream>
#include <numeric>
#include <vector>

int main() {
    std::vector<int> v = {4, 7, 1, 8, 6};
    auto is_even = [](int n) { return n % 2 == 0; };
    int threshold = 5;
    auto over = [threshold](int n) { return n > threshold; };   // a copy of 5
    int count = 0;
    auto tally = [&count](int n) { count += n; };               // the real count

    std::for_each(v.begin(), v.end(), tally);
    std::cout << std::count_if(v.begin(), v.end(), is_even) << " "
              << std::count_if(v.begin(), v.end(), over) << " "
              << count << " " << std::accumulate(v.begin(), v.end(), 0) << "\n";

    threshold = 0;       // `over` kept its own copy, so nothing changes
    std::cout << std::count_if(v.begin(), v.end(), over) << "\n";
}
```

```output
3 3 26 26
3
```

The argument for using these over a hand-written loop is not speed — it is that
the name says what the loop does. `std::any_of` cannot accidentally be an
`all_of`, and it cannot have an off-by-one.

C++20 adds the ranges versions, which take the container directly:
`std::ranges::sort(v)`.

## Your turn

In `algo.h` — everything is a template, so everything is here:

- `template <typename T> T largest(const std::vector<T>& values)` — throws
  `std::invalid_argument` when empty
- `template <typename T, typename Pred> int count_if_matching(const std::vector<T>&, Pred)`
- `template <typename T, typename F> auto transform_all(const std::vector<T>&, F)`
  — a vector of the results
- `template <typename T> T sum_all(const std::vector<T>& values, T initial)`
