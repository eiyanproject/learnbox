---
title: Classes, constructors and RAII
summary: A destructor that runs on the way out of scope, what that buys you, and the rule of zero.
order: 2
files: [counter.cpp, counter.h]
run: g++ -std=c++20 -Wall counter.cpp -o counter && ./counter
hints:
  - "`Counter` holds a private int. The constructor takes an optional starting value - give it a default argument of 0."
  - "Mark `value()` as `const`: it does not modify the object, and only a const member function can be called on a const object."
  - "`Tracker` increments a counter it is given a reference to, and decrements it in its destructor - that is the RAII pattern being demonstrated."
  - "Store the reference as a member: `int& count_;` initialised in the constructor's initialiser list, because a reference cannot be assigned later."
---

A class bundles data with the operations on it, and adds one thing C does not
have: a **destructor** that runs automatically when the object goes out of
scope.

```cpp
class Counter {
public:
    explicit Counter(int start = 0) : value_(start) {}

    void increment() { value_++; }
    int value() const { return value_; }

private:
    int value_;
};
```

## The initialiser list

```cpp
Counter(int start) : value_(start) {}     // initialises
Counter(int start) { value_ = start; }    // default-constructs, then assigns
```

The first initialises the member directly; the second builds it and then
overwrites it. For an `int` the difference is nothing, for a `std::string` it
is wasted work, and for a `const` member or a reference the second form does
not compile at all — they can only be initialised, never assigned.

## const member functions

```cpp
int value() const;
```

`const` after the parameter list promises the function does not modify the
object. It is not decoration: a `const Counter&` — which is how objects are
usually passed — can only have its `const` members called. Forgetting it is why
"why can't I call this on a const reference" happens.

## explicit

```cpp
explicit Counter(int start = 0);
```

Without `explicit`, a one-argument constructor is an implicit conversion, and
`Counter c = 5;` compiles. That is rarely what anyone wants, and the surprises
it causes are worse than the typing it saves.

## RAII

The destructor runs when the object leaves scope — on a normal exit, on an
early `return`, and while an exception is unwinding:

```cpp
{
    Tracker t(active);     // constructor: active++
    ...                    // even if this throws
}                          // destructor: active--
```

That guarantee is what makes `std::vector`, `std::string`, `std::lock_guard`
and `std::unique_ptr` safe. Each owns a resource, and the destructor releases
it, so there is no code path that forgets.

## The rule of zero

If your class does not manage a raw resource, write no destructor, no copy
constructor and no assignment operator. The compiler-generated ones do the
right thing, and members that manage themselves (like `vector`) handle the
rest. Writing them by hand is how you acquire bugs you did not need.

## Your turn

In `counter.h` and `counter.cpp`:

- `class Counter` — `explicit Counter(int start = 0)`, `increment()`,
  `add(int)`, `int value() const`, `void reset()`
- `class Tracker` — constructed with `int&`, increments it, and decrements it
  in its destructor
