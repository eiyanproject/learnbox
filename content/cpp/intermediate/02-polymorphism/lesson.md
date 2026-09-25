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
removes it entirely.

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
