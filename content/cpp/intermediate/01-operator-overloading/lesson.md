---
title: Operator overloading and value semantics
summary: Making your type behave like a built-in, which operators to write as members and which as free functions, and the symmetry rule.
order: 1
files: [money.h]
run: g++ -std=c++20 -Wall -fsyntax-only money.h && echo "header compiles"
hints:
  - "`operator+` should be a free function, not a member: a member requires the left operand to be your type, which breaks symmetry."
  - "Write `operator+` in terms of `operator+=` - the member does the work, the free function copies and delegates."
  - "`operator==` can be defaulted in C++20: `bool operator==(const Money&) const = default;` compares every member."
  - "`operator<<` takes `std::ostream&` and returns it so the calls chain; it must be a free function because the stream is the left operand."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **operator overloading** | giving your type its own meaning for `+`, `==`, `<<` |
| **value semantics** | a type that behaves like a number: copied, compared, combined |
| **member operator** | defined inside the class; the left operand must be the class |
| **free function** | defined outside the class; both operands are parameters, so it is symmetric |
| **operand** | a value an operator works on: `lhs` (left) and `rhs` (right) |
| **canonical pair** | `+=` as a member, `+` as a free function built on it |
| **`*this`** | the object a member function was called on |
| **elide** | the compiler skipping a copy |
| **`friend`** | a free function allowed to see the class's private members |
| **memberwise** | comparing every member in order |
| **spaceship operator** | `<=>`: one definition that generates `<`, `>`, `<=`, `>=` |
| **`std::strong_ordering`** | the result type of `<=>` for values that are fully ordered |
| **cents** | money held as a whole number of cents, so there is no rounding |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `g++ -std=c++20 -Wall -fsyntax-only money.h && echo "header compiles"` | checks the header compiles, without building anything |
| `-fsyntax-only` | check the code, produce no output file |

### C++ names

| Name | What it does |
|---|---|
| `Money& operator+=(const Money& rhs) { ...; return *this; }` | a modifying member operator |
| `friend Money operator+(Money lhs, const Money& rhs)` | binary `+`, taking the left by value |
| `bool operator==(const Money&) const = default;` | generated equality, and `!=` |
| `std::strong_ordering operator<=>(const Money&) const = default;` | generated ordering |
| `#include <compare>` | declares the ordering types |
| `std::ostream& operator<<(std::ostream& os, const Money& m)` | lets `std::cout << money` work |
| `explicit Money(long cents = 0)` | no implicit conversion from a number |

---

C++ lets your types use the same syntax as built-in ones. Used well that
removes noise; used badly it hides surprises behind familiar symbols.

## Member or free function

```cpp
class Money {
    Money& operator+=(const Money& other);    // member: modifies this
};

Money operator+(Money left, const Money& right);   // free: symmetric
```

The rule follows from how the left operand is treated. A **member** operator
requires the left operand to be your class, so `2 * money` cannot work if
`operator*` is a member — only `money * 2`. A free function takes both operands
as parameters and is symmetric.

So: operators that modify (`+=`, `-=`, `++`) are members; binary arithmetic
(`+`, `-`, `*`) and comparisons are free functions.

## The canonical pair

```cpp
Money& operator+=(const Money& rhs) { amount_ += rhs.amount_; return *this; }

friend Money operator+(Money lhs, const Money& rhs) { lhs += rhs; return lhs; }
```

`operator+` takes its left operand **by value** — that copy is the result — and
delegates to `+=`. The logic lives in one place, and the copy is one the
compiler often elides anyway.

Returning `*this` from `+=` is what makes `a += b += c` work and matches what
the built-in types do.

## Comparisons

C++20 collapses this:

```cpp
bool operator==(const Money&) const = default;      // memberwise
std::strong_ordering operator<=>(const Money&) const = default;
```

The spaceship operator generates `<`, `>`, `<=` and `>=` from one definition,
and `==` generates `!=`. Before C++20 you wrote six; now you write one or two.

All of it in one small class:

```cpp
#include <compare>
#include <iostream>

class Money {
public:
    explicit Money(long cents) : cents_(cents) {}
    Money& operator+=(const Money& rhs) { cents_ += rhs.cents_; return *this; }
    friend Money operator+(Money lhs, const Money& rhs) { lhs += rhs; return lhs; }
    bool operator==(const Money&) const = default;
    std::strong_ordering operator<=>(const Money&) const = default;
    long cents() const { return cents_; }

private:
    long cents_;
};

int main() {
    Money a(150), b(250);
    Money c = a + b;
    std::cout << c.cents() << " " << a.cents() << "\n";    // a is untouched
    std::cout << (a < b) << (a >= b) << (c != Money(400)) << "\n";
}
```

```output
400 150
100
```

## When not to

An overloaded operator should mean what the symbol means. `+` on a collection
that *removes* things is legal and indefensible. The test is whether a reader
who has not seen your class can predict what it does — which is why `<<` for
output is fine (everyone knows it) and `%` for "format" is not.

## Your turn

In `money.h`, a `Money` holding cents as a `long`:

- `explicit Money(long cents = 0)`, `long cents() const`
- `operator+=` and `operator-=` as members
- `operator+` and `operator-` as free functions
- `operator*` by an integer, both orders
- `operator==` and `operator<=>`, defaulted
- `operator<<` writing `"$12.34"`
