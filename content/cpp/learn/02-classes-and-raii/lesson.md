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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **class** | bundles data with the operations on it |
| **member** | a variable (data member) or function (member function) of a class |
| **`public`** / **`private`** | usable from outside / only inside the class |
| **constructor** | runs when an object is created |
| **default argument** | `int start = 0`: used when the caller gives none |
| **initialiser list** | `: value_(start)`: initialises members directly |
| **default-construct** | build with no arguments |
| **`const` member function** | promises not to modify the object; callable on a `const&` |
| **`explicit`** | stops a one-argument constructor being an implicit conversion |
| **implicit conversion** | the compiler converting a value silently, as in `Counter c = 5;` |
| **destructor** | `~Name()`: runs when the object leaves scope |
| **stack unwinding** | destructors running as an exception travels up |
| **rule of zero** | if a class owns no raw resource, write no destructor, copy constructor or assignment |
| **trailing underscore** | `value_`: a common naming habit for data members |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `g++ -std=c++20 -Wall counter.cpp -o counter && ./counter` | compiles and runs |

### C++ names

| Name | What it does |
|---|---|
| `class Counter { public: ... private: ... };` | a class |
| `explicit Counter(int start = 0) : value_(start) {}` | a constructor with an initialiser list |
| `int value() const` | a const member function |
| `~Tracker() { active--; }` | a destructor |
| `struct` | a class whose members are public by default |
| `int&` | a reference parameter the class can keep and change |
| `throw std::runtime_error("boom")` | throws an exception |
| `catch (const std::exception& e)`, `e.what()` | catches it; its message |
| `std::lock_guard`, `std::unique_ptr` | standard RAII classes |

### Errors

| Error | Means |
|---|---|
| `passing 'const Counter' as 'this' argument discards qualifiers` | calling a non-const member on a const object |
| `uninitialized const member` / `uninitialized reference member` | a const or reference member not set in the initialiser list |

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

Watch the count go back down while an exception is in flight:

```cpp
#include <iostream>
#include <stdexcept>

int active = 0;

struct Tracker {
    Tracker() { active++; }
    ~Tracker() { active--; }
};

int main() {
    try {
        Tracker t;
        std::cout << "inside: " << active << "\n";
        throw std::runtime_error("boom");
    } catch (const std::exception& e) {
        std::cout << "after " << e.what() << ": " << active << "\n";
    }
}
```

```output
inside: 1
after boom: 0
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
