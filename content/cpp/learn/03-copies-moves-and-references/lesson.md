---
title: Copies, moves and references
summary: What passing by value actually costs, how a move avoids it, and the three ways to take a parameter.
order: 3
files: [move.cpp, move.h]
run: g++ -std=c++20 -Wall move.cpp -o move && ./move
hints:
  - "`Buffer` holds a std::vector<int> and counts how many times it was copied and moved - make those counters static so the tests can read them."
  - "The copy constructor takes `const Buffer&`; the move constructor takes `Buffer&&` and should be marked noexcept."
  - "In the move constructor use `std::move(other.data_)` - without it you would copy the vector, which is the whole mistake being demonstrated."
  - "`std::move` does not move anything; it casts to an rvalue reference so the move constructor is chosen. Include <utility>."
---

C++ copies by default. Understanding when it does, and how to say "do not", is
most of what separates fast C++ from slow C++.

## Three ways to take a parameter

```cpp
void a(Buffer b);          // a copy - the caller's stays intact
void b(const Buffer& b);   // no copy, cannot modify
void c(Buffer& b);         // no copy, can modify
```

`const&` is the default for anything bigger than a pointer. By value is for
small things, or when the function needs its own copy anyway.

## Moving

A move transfers ownership instead of duplicating:

```cpp
Buffer a = make();
Buffer b = std::move(a);   // b takes a's storage; a is left valid but empty
```

For a `vector`, a copy allocates and copies every element; a move steals the
pointer. Same result, unmeasurably cheaper.

**`std::move` does not move anything.** It is a cast that says "I am done with
this", which lets the compiler pick the move constructor instead of the copy
one. After it, the source is in a *valid but unspecified* state — you may
destroy it or assign to it, but you should not read it expecting the old value.

## Writing them

```cpp
Buffer(const Buffer& other) : data_(other.data_) {}            // copy
Buffer(Buffer&& other) noexcept : data_(std::move(other.data_)) {}  // move
```

`Buffer&&` is an rvalue reference: it binds to temporaries and to anything
`std::move`d. The `noexcept` matters — `std::vector` will only *move* your type
when it reallocates if the move constructor promises not to throw, and will
copy it otherwise.

Note `std::move(other.data_)` inside the move constructor. `other` is an rvalue
reference, but `other.data_` is a named thing and therefore an lvalue; without
the `std::move` you would silently copy.

## Rule of zero, again

Almost never write these. A class made of `vector`, `string` and `unique_ptr`
members gets correct copy and move operations for free. This lesson writes them
by hand so you can see what the compiler is doing on your behalf.

## Your turn

In `move.h` and `move.cpp`, a `Buffer` wrapping a `std::vector<int>`:

- `explicit Buffer(std::size_t n)` — n zeroes
- a copy constructor that increments `Buffer::copies`
- a move constructor, `noexcept`, that increments `Buffer::moves`
- `std::size_t size() const`
- `static int copies` and `static int moves`, and
  `static void reset_counts()`
