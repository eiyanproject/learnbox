---
title: Smart pointers and ownership
summary: unique_ptr as the default, shared_ptr where ownership is genuinely shared, and why new and delete should not appear in your code.
order: 5
files: [own.cpp, own.h]
run: g++ -std=c++20 -Wall own.cpp -o own && ./own
hints:
  - "`std::make_unique<Node>(value)` allocates and wraps in one step - prefer it to `std::unique_ptr<Node>(new Node(value))`."
  - "A unique_ptr cannot be copied, only moved: `list.push_back(std::move(node))`."
  - "`Node` counts live instances with a static int incremented in the constructor and decremented in the destructor - that is how the tests prove nothing leaked."
  - "`total` walks the vector with `const auto&` and reads `node->value` - the arrow works on a smart pointer exactly as on a raw one."
---

Raw `new` and `delete` are almost never correct in modern C++, because you
cannot see every path out of a function — early returns and exceptions both
skip the `delete`.

## unique_ptr

```cpp
auto node = std::make_unique<Node>(42);
node->value;       // like a raw pointer
```

Exactly one `unique_ptr` owns the object. When it goes out of scope, the object
is destroyed — on every path, including an exception. There is no reference
count and no overhead: it is the size of a pointer and compiles to the same
code you would have written by hand, correctly.

Because ownership is unique, a `unique_ptr` **cannot be copied**, only moved:

```cpp
auto b = std::move(a);      // a is now empty
list.push_back(std::move(node));
```

That restriction is the feature: the compiler refuses the code that would have
produced a double free.

## make_unique

```cpp
auto p = std::make_unique<Node>(42);          // preferred
std::unique_ptr<Node> q(new Node(42));        // works, but
```

`make_unique` is one allocation, it is exception-safe in argument lists, and it
says the type once instead of twice.

## shared_ptr

```cpp
auto a = std::make_shared<Node>(1);
auto b = a;        // both own it; the count is 2
```

Reference counted: destroyed when the last owner goes. Use it when ownership is
genuinely shared and you cannot say who outlives whom — a graph, a cache, a
callback registry.

It costs an atomic increment per copy and a second allocation for the control
block (unless you use `make_shared`, which combines them). Two `shared_ptr`s
pointing at each other never reach zero, which is what `std::weak_ptr` exists
to break.

## Which to reach for

| Situation | |
|---|---|
| one owner | `unique_ptr` — the default |
| genuinely shared | `shared_ptr` |
| observing, not owning | a raw `T*` or a reference |
| a cycle to break | `weak_ptr` |

A raw pointer is still fine as a **non-owning** parameter. The rule is not "no
raw pointers", it is "raw pointers do not own".

## Your turn

In `own.h` and `own.cpp`:

- `struct Node` with an `int value`, a constructor, and `static int live` that
  the constructor increments and the destructor decrements
- `std::unique_ptr<Node> make_node(int value)`
- `std::vector<std::unique_ptr<Node>> make_nodes(int n)` — values 0..n-1
- `int total(const std::vector<std::unique_ptr<Node>>& nodes)`
- `std::unique_ptr<Node> take_largest(std::vector<std::unique_ptr<Node>>& nodes)`
  — removes and returns the node with the largest value, or `nullptr`
