---
title: Virtual functions and interfaces
summary: Dynamic dispatch through a base pointer, the virtual destructor that is not optional, and when to prefer a variant instead.
order: 2
files: [shapes.h]
run: g++ -std=c++20 -Wall -fsyntax-only shapes.h && echo "header compiles"
hints:
  - "`virtual double area() const = 0;` makes Shape abstract - a pure virtual function has no body and cannot be instantiated."
  - "The base class needs `virtual ~Shape() = default;` - without it, deleting through a base pointer is undefined behaviour."
  - "Mark overrides with `override`: it is checked, so a signature that does not actually override becomes a compile error instead of a silent second function."
  - "`total_area` takes `const std::vector<std::unique_ptr<Shape>>&` and sums through the base pointers - that is the dispatch being tested."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **polymorphism** | one interface, many types behind it |
| **virtual function** | dispatched on the object's runtime type, not the pointer's declared type |
| **runtime type** / **declared type** | what the object really is / what the pointer says |
| **pure virtual** | `= 0`: no body; the class cannot be instantiated |
| **interface** | a class of pure virtual functions |
| **base** / **derived class** | the general class / one that inherits from it |
| **inheritance** | `class Circle : public Shape`: a derived class gets the base's interface |
| **virtual destructor** | needed so deleting through a base pointer destroys the whole object |
| **`override`** | asks the compiler to check that a function really overrides one |
| **signature** | a function's name, parameters and `const`; a mismatch defines a new function |
| **hide** | a derived function with the same name masking the base one |
| **vtable** | the table of function pointers each object points to |
| **indirect call** | a call through a pointer, which the CPU cannot predict well |
| **closed set of types** | all types known in advance; `std::variant` fits |
| **exhaustiveness** | the compiler checking every case is handled |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `g++ -std=c++20 -Wall -fsyntax-only shapes.h && echo "header compiles"` | checks the header compiles, without building anything |
| `-fsyntax-only` | check the code, produce no output file |

### C++ names

| Name | What it does |
|---|---|
| `virtual ~Shape() = default;` | a virtual destructor |
| `virtual double area() const = 0;` | a pure virtual function |
| `double area() const override;` | an override the compiler checks |
| `std::vector<std::unique_ptr<Shape>>` | a list of owned shapes of any kind |
| `std::make_unique<Circle>(...)` | creates one |
| `std::variant`, `std::visit` | a closed set of types, and calling code for whichever one is held |

### Errors

| Error | Means |
|---|---|
| `marked 'override', but does not override` | the signature does not match any base function |
| `cannot declare variable to be of abstract type` | creating an object of a class with pure virtual functions |

---

A virtual function is dispatched on the **runtime** type of the object rather
than the declared type of the pointer.

```cpp
class Shape {
public:
    virtual ~Shape() = default;
    virtual double area() const = 0;
    virtual std::string name() const = 0;
};
```

`= 0` makes a function **pure virtual**: no body, and the class cannot be
instantiated. That is how C++ writes an interface.

## The virtual destructor

```cpp
Shape* s = new Circle(2);
delete s;        // without a virtual destructor: undefined behaviour
```

Deleting through a base pointer calls the base destructor only, so the derived
part is never destroyed — the classic leak. The rule is simple and absolute:
**any class used polymorphically needs a virtual destructor**, and `= default`
is enough.

The same applies to `std::unique_ptr<Shape>`, which calls `delete` on the base
pointer.

## override

```cpp
double area() const override;
```

`override` asks the compiler to check. Without it, a mismatched signature —
a missing `const`, a different parameter type — silently defines a *new*
function that hides nothing and overrides nothing, and your calls go to the
base version. This is one of the most annoying bugs in C++ and `override`
removes it entirely. Here is the bug, with `Typo` missing a `const`:

```cpp
#include <iostream>
#include <memory>
#include <string>
#include <vector>

struct Shape {
    virtual ~Shape() = default;
    virtual std::string name() const { return "shape"; }
};

struct Circle : Shape {
    std::string name() const override { return "circle"; }
};

struct Typo : Shape {
    std::string name() { return "typo"; }    // no const: a NEW function
};

int main() {
    std::vector<std::unique_ptr<Shape>> shapes;
    shapes.push_back(std::make_unique<Circle>());
    shapes.push_back(std::make_unique<Typo>());
    for (const auto& s : shapes) std::cout << s->name() << "\n";
}
```

```output
circle
shape
```

Add `override` to `Typo::name` and it no longer compiles - which is the
point.

## The cost

A virtual call is an indirect call through a table pointer stored in each
object. That is a pointer per object and a hard-to-predict jump per call.
Usually irrelevant; occasionally the whole problem in a tight loop.

## When not to use it

If the set of types is **closed and known**, `std::variant` plus
`std::visit` gives compile-time exhaustiveness, no allocation and no
indirection. Inheritance earns its cost when the set is open — when callers
will add types you have not seen.

## Your turn

In `shapes.h`:

- `class Shape` — virtual destructor, pure virtual `area()` and `name()`, and
  a non-virtual `describe()` returning `"<name>: <area>"`
- `class Circle : public Shape` and `class Rect : public Shape`
- `double total_area(const std::vector<std::unique_ptr<Shape>>&)`
- `const Shape* largest(const std::vector<std::unique_ptr<Shape>>&)` — nullptr
  when empty
