---
title: Reporting failure
summary: Exceptions, std::optional and std::expected - three answers to "this might not work", and when each is the right one.
order: 3
files: [parse.h]
run: g++ -std=c++20 -Wall -fsyntax-only parse.h && echo "header compiles"
hints:
  - "`parse_int` returns `std::optional<int>`: `std::nullopt` when the text is not a number, the value otherwise."
  - "Use `std::from_chars` if you like, but a simple loop is fine - the point is the return type, not the parsing."
  - "`divide` throws std::domain_error for a zero divisor: the caller cannot sensibly continue, which is what an exception is for."
  - "`parse_all` collects the successes and returns how many failed through an out-parameter, so one bad entry does not lose the rest."
---

Three mechanisms, three different situations.

## Exceptions

```cpp
if (divisor == 0) throw std::domain_error("division by zero");
```

For failures the immediate caller usually cannot handle — a broken invariant, a
resource that will not open, a bug. The cost is paid only when one is thrown,
and the benefit is that the error cannot be ignored: there is no return value
to forget to check.

Against them: they are invisible at the call site, they need RAII everywhere to
be safe, and some domains ban them outright (embedded, games, parts of
systems programming).

**A destructor must never throw.** If one throws while another exception is
unwinding, the program terminates. Destructors are `noexcept` by default for
this reason.

## std::optional

```cpp
std::optional<int> parse_int(std::string_view text);
```

For "there might be no value, and that is normal". A lookup that misses, a
parse that fails on user input, the first element of an empty collection.

```cpp
if (auto n = parse_int(text)) { use(*n); }
value_or(0);
```

It says in the type that absence is possible, so the caller cannot ignore it
the way they ignore a `-1` return.

## std::expected

C++23 adds `std::expected<T, E>` — a value **or** an error, with the error
carrying information:

```cpp
std::expected<int, ParseError> parse(std::string_view);
```

`optional` says it failed; `expected` says why. Where the caller needs to
distinguish "not a number" from "out of range", that difference matters.

## Choosing

| Situation | |
|---|---|
| Absence is normal and the reason does not matter | `optional` |
| Absence is normal and the reason matters | `expected` |
| The caller cannot reasonably continue | throw |
| A programming error | `assert`, or throw |

The common mistake is throwing for ordinary control flow — a failed lookup is
not exceptional, and making it one is both slow and noisy.

## Your turn

In `parse.h`:

- `std::optional<int> parse_int(std::string_view text)` — digits with an
  optional leading `-`
- `int divide(int a, int b)` — throws `std::domain_error` when `b` is zero
- `std::vector<int> parse_all(const std::vector<std::string>& items, int* failed)`
- `int parse_or(std::string_view text, int fallback)`
