---
title: Concepts and constraints
summary: Saying what a template requires, so the compiler rejects the wrong type at the call and not two hundred lines deep inside your code.
order: 2
files: [shapes2.h]
run: g++ -std=c++20 -Wall -fsyntax-only shapes2.h && echo "header compiles"
hints:
  - "`concept Numeric = std::integral<T> || std::floating_point<T>;` - concepts compose with && and || like ordinary boolean expressions."
  - "A requires-expression checks that an expression compiles: `requires(const T& t) { { t.name() } -> std::convertible_to<std::string>; }`."
  - "Constrain with `template <Numeric T>` - shorthand for `template <typename T> requires Numeric<T>`."
  - "`describe` uses `if constexpr (Numeric<T>)`: the branch not taken is not compiled, so each branch may only be valid for its own type."
---

Before C++20, a template said nothing about what it needed. Pass the wrong
type and the error appeared wherever the code first failed — often deep inside
the standard library, hundreds of lines of it, naming types you never wrote.

A concept moves that error to the call site and states the requirement in
words.

## Defining one

```cpp
template <typename T>
concept Numeric = std::integral<T> || std::floating_point<T>;
```

A concept is a compile-time predicate on types. They compose with `&&`, `||`
and `!` exactly as you would expect.

## requires-expressions

To demand that something *works* rather than that the type is a specific one:

```cpp
template <typename T>
concept Named = requires(const T& t) {
    { t.name() } -> std::convertible_to<std::string>;
};
```

This says: given a `const T&`, `t.name()` must compile, and its result must
convert to `std::string`. Nothing is called and nothing is evaluated — the
compiler only checks that the expression is well-formed.

This is duck typing, checked at compile time and stated up front.

## Using one

```cpp
template <Numeric T> T sum(const std::vector<T>& v);
```

is shorthand for `template <typename T> requires Numeric<T>`. Call it with
`std::vector<std::string>` and the error is *"constraint not satisfied"* at
your call — one line, naming the concept.

## if constexpr

```cpp
if constexpr (Numeric<T>) {
    return std::to_string(value);
} else {
    return value.name();
}
```

The branch not taken is **discarded, not compiled**. That is what makes this
different from a normal `if`: `value.name()` would be a hard error for an
`int`, and here it never reaches the compiler. One function, two types, no
overloads.

## Overload resolution

Given two candidates, the compiler prefers the **more constrained** one. So a
generic `print(const T&)` and a `print(Named auto const&)` coexist, and the
specific one wins for types that satisfy it — without the tag-dispatch or
SFINAE that this used to require.

## Your turn

In `shapes2.h`:

- `concept Numeric` and `concept Named`
- `template <Numeric T> T sum(const std::vector<T>& values)`
- `template <Named T> std::string label(const T& item)` — `"[name]"`
- `template <typename T> std::string describe(const T& value)` — `if constexpr`
- `template <Numeric T> T clamp_to(T value, T lo, T hi)`
