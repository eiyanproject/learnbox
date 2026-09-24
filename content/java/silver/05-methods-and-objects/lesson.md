---
title: Methods, overloading and objects
summary: Overload resolution, static against instance, constructor chaining, and the fact that Java always passes by value.
order: 5
files: [Account.java]
run: javac Account.java && java Account
hints:
  - "Two constructors: `Account(String owner)` opens with a zero balance and should call `this(owner, 0)` rather than repeat the assignments."
  - "`this(...)` must be the FIRST statement in a constructor, and only one constructor may call another that way."
  - "`deposit` should reject a non-positive amount with IllegalArgumentException; `withdraw` should reject more than the balance."
  - "`transferTo` moves money between two accounts: withdraw here, deposit there, and let the exceptions propagate if either refuses."
---

## Overloading

Several methods can share a name if their **parameter lists** differ:

```java
int add(int a, int b)
double add(double a, double b)
int add(int... values)
```

The compiler picks one from the argument types, at compile time. Two rules
matter:

- **The return type is not part of the signature.** Two methods differing only
  in return type do not compile.
- **Resolution prefers the most specific match**, and tries in order: exact
  match, then widening, then boxing, then varargs. So `add(1, 2)` picks the
  `int` version, and varargs is the last resort — which is why adding a varargs
  overload rarely breaks existing calls.

## static against instance

`static` belongs to the class; instance members belong to an object.

```java
static int count;         // one, shared
private double balance;   // one per account
```

A static method cannot use `this` and cannot touch instance fields, because
there is no instance. The error — "non-static variable cannot be referenced
from a static context" — means exactly that, and it is what `main` hits when
someone tries to use a field from it.

## Constructors

A constructor has the class's name and no return type. If you write none, Java
gives you a no-argument default — **but only if you write none at all**. Add
any constructor and the free one disappears, which breaks `new Thing()` in a
way that reads like a bug.

Chain them with `this(...)` to keep the logic in one place:

```java
public Account(String owner) {
    this(owner, 0);          // must be the first statement
}
```

`this(...)` calls a sibling constructor; `super(...)` calls the parent's. A
constructor can use one or the other, first, never both.

## Pass by value, always

Java passes everything by value. For an object, the **reference** is copied:

```java
void rename(Account a) { a.setOwner("x"); }   // caller sees the change
void replace(Account a) { a = new Account(); } // caller sees nothing
```

The first mutates the object both references point at. The second repoints the
local copy and the caller's reference is untouched. "Java is pass by reference"
is a persistent myth; the exam tests the difference above directly.

## Your turn

In `Account.java`:

- `private final String owner` and `private double balance`
- `Account(String owner, double balance)` and `Account(String owner)` which
  chains to it with a balance of 0
- `getOwner()`, `getBalance()`
- `deposit(double)` — `IllegalArgumentException` if not positive
- `withdraw(double)` — `IllegalArgumentException` if not positive or more than
  the balance
- `transferTo(Account other, double amount)`
