---
title: Work done at compile time
summary: constexpr, consteval and static_assert - moving computation and checking out of the running program and into the build.
order: 3
files: [ct.h]
run: g++ -std=c++20 -Wall -fsyntax-only ct.h && echo "header compiles"
hints:
  - "`constexpr` means *may* run at compile time; write it as an ordinary function and the compiler decides based on the arguments."
  - "`consteval` means *must*. Calling it with a runtime value is a compile error, which is the point."
  - "`make_squares<N>()` returns a std::array<int, N> built with a loop - loops are allowed in a constexpr function since C++14."
  - "static_assert is the proof: if `factorial(5)` were not computable at compile time, `static_assert(factorial(5) == 120)` would not compile."
---

Anything the compiler can work out, the running program does not have to.

## constexpr

```cpp
constexpr int factorial(int n) {
    return n <= 1 ? 1 : n * factorial(n - 1);
}
```

`constexpr` on a function means **may** be evaluated at compile time. Called
with a constant it folds to a literal; called with a runtime value it is an
ordinary function. One definition serves both.

Since C++14 these are ordinary functions inside — loops, local variables,
`if`. The restriction is only that they cannot do anything the compiler cannot
do: no I/O, no `new` that outlives the evaluation, no undefined behaviour.

That last one is quietly valuable. Undefined behaviour in a constant
expression is a **compile error**, not a silent miscompile. `constexpr int x =
1 << 40;` does not build.

## consteval

```cpp
consteval int checked_percent(int n);
```

**Must** be evaluated at compile time. Pass a runtime value and it fails to
compile. Use it when running the function at run time would defeat the purpose
— a validated literal, a compile-time hash, a format string check.

## constinit

```cpp
constinit int counter = compute();
```

Guarantees the initialisation happens at compile time, without also making the
variable `const`. It exists to rule out the static initialisation order fiasco:
the value is baked into the binary, so no ordering question arises.

## Tables

```cpp
constexpr auto squares = make_squares<16>();
```

A lookup table computed by the compiler and emitted as data. No startup cost,
no initialisation order, and usable in other constant expressions.

## static_assert

```cpp
static_assert(factorial(5) == 120);
static_assert(sizeof(void*) == 8, "64-bit only");
```

A test that runs at compile time and costs nothing at run time. If the
expression is not a constant expression, it does not compile — which is why a
`static_assert` is also the proof that a `constexpr` function really is one.

## Your turn

In `ct.h`:

- `constexpr int factorial(int n)`
- `constexpr int fib(int n)`
- `constexpr std::size_t length(const char* s)`
- `consteval int checked_percent(int n)` — 0..100, else a compile error
- `template <std::size_t N> constexpr std::array<int, N> make_squares()`
