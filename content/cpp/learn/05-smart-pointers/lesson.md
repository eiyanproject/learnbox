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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **raw pointer** | a plain `T*`; should not own |
| **smart pointer** | an object that owns a heap object and deletes it |
| **`unique_ptr`** | exactly one owner; moved, never copied; no overhead |
| **`shared_ptr`** | reference counted: destroyed when the last owner goes |
| **reference count** | how many owners share an object |
| **control block** | where a `shared_ptr` keeps the count |
| **atomic increment** | adding one safely across threads; what each `shared_ptr` copy costs |
| **cycle** | two `shared_ptr`s pointing at each other, never reaching zero |
| **`weak_ptr`** | observes a shared object without owning it; breaks cycles |
| **non-owning** | a pointer or reference that only observes |
| **exception-safe** | no leak even if something throws |
| **double free** | deleting twice; `unique_ptr`'s no-copy rule prevents it |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `g++ -std=c++20 -Wall own.cpp -o own && ./own` | compiles and runs |

### C++ names

| Name | What it does |
|---|---|
| `#include <memory>` | the smart pointers |
| `std::make_unique<Node>(42)` | creates an owned `Node` |
| `node->value` | a member through the pointer |
| `auto b = std::move(a);` | transfers ownership; `a` becomes empty |
| `std::make_shared<Node>(1)` | creates a shared `Node`, one allocation |
| `s.use_count()` | how many owners |
| `t.reset()` | gives up ownership |
| `nullptr` | the null pointer |
| `std::vector<std::unique_ptr<Node>>` | a vector that owns its nodes |

### Errors

| Error | Means |
|---|---|
| `use of deleted function 'std::unique_ptr<...>::unique_ptr(const std::unique_ptr<...>&)'` | trying to copy a `unique_ptr`; move it instead |

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

```cpp
#include <iostream>
#include <memory>

struct Node {
    int value;
    explicit Node(int v) : value(v) {}
};

int main() {
    auto a = std::make_unique<Node>(42);
    auto b = std::move(a);
    std::cout << "a empty: " << (a == nullptr) << ", b: " << b->value << "\n";

    auto s = std::make_shared<Node>(1);
    auto t = s;
    std::cout << "owners: " << s.use_count() << "\n";
    t.reset();
    std::cout << "owners: " << s.use_count() << "\n";
}
```

```output
a empty: 1, b: 42
owners: 2
owners: 1
```

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
