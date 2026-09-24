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
