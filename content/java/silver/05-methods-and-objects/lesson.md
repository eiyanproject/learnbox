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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **object** | a value that bundles data (fields) with the code that works on it (methods) |
| **class** | the blueprint objects are made from |
| **field** | a variable belonging to a class or to each object |
| **method** | a named block of code belonging to a class |
| **parameter list** | the types of a method's parameters, in order |
| **overloading** | several methods with one name and different parameter lists |
| **signature** | a method's name plus its parameter types; the return type is not part of it |
| **overload resolution** | the compiler's choice: exact match, then widening, then boxing, then varargs |
| **boxing** / **unboxing** | wrapping a primitive in its object type (`int` to `Integer`) / unwrapping it |
| **wrapper class** | the object type of a primitive: `Integer`, `Double`, `Boolean`... |
| **static member** | belongs to the class: one shared copy, used as `Account.count` |
| **instance member** | belongs to each object: every account has its own `balance` |
| **`this`** | the object the current method was called on |
| **static context** | inside a static method, where there is no `this` |
| **constructor** | code that runs on `new` to set up the fields; the class's name and no return type |
| **default constructor** | the free no-argument constructor, given only if you write none |
| **constructor chaining** | one constructor calling another with `this(...)`, as its first statement |
| **`super(...)`** | calls the parent class's constructor |
| **class hierarchy** | a class, its parent, the parent's parent, up to `Object` |
| **reference** | in effect an object's address; an object variable holds one, not the object |
| **pass by value** | a method gets a copy of each argument; for objects, a copy of the reference |
| **mutate** vs **repoint** | change the shared object vs make the local copy refer to another one |
| **nested class** | a class declared inside another; `static` means no outer object is needed |
| **propagate** | an exception passing on to the caller because nothing caught it |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `javac Account.java && java Account` | builds and runs this lesson's file |

### Java keywords, classes and methods

| Name | What it does |
|---|---|
| `int add(int a, int b)` / `double add(double a, double b)` | two overloads of one name |
| `static int count;` | one field shared by the whole class |
| `private double balance;` | one field per object |
| `private final String owner;` | set once in the constructor, never reassigned |
| `public Account(String owner, double balance)` | a constructor |
| `this(owner, 0);` | runs the other constructor, here with a balance of 0 |
| `new Account("ada")` | creates an object and gives back a reference to it |
| `Integer.valueOf(5)` | boxes 5 into an `Integer` |
| `acc.owner` | a field of the object `acc` refers to |
| `throw new IllegalArgumentException("amount must be positive");` | rejects a bad value |

### Errors

| Error | Means |
|---|---|
| `non-static variable count cannot be referenced from a static context` | a static method (such as `main`) used an instance field |
| `constructor St in class St cannot be applied to given types` | no constructor matches those arguments, often because the free one disappeared |
| `IllegalArgumentException` | thrown on purpose for an amount that is not allowed |

---

An object bundles data (its **fields**) with the code that works on it (its
**methods**), and a class is the blueprint objects are made from. This lesson
covers how methods are chosen when several share a name, the difference
between what belongs to the class and what belongs to each object, how
objects are set up by constructors, and what really happens when you pass an
object to a method, which is the subject of one of Java's most persistent
myths.

## Overloading

Several methods can share a name if their **parameter lists** differ. This is
**overloading**, and it lets one name cover what is conceptually one
operation on different kinds of input, as `System.out.println` does for
numbers, strings and everything else:

```java
int add(int a, int b)
double add(double a, double b)
int add(int... values)
```

(Method headers only.) The compiler picks one from the argument types, at
compile time: `add(1, 2)` and `add(1.5, 2.5)` call different methods. The
name plus the parameter types is the method's **signature**, and signatures
must be unique within a class. Two rules matter:

- **The return type is not part of the signature.** Two methods differing only
  in return type do not compile.
- **Resolution prefers the most specific match**, and tries in order: exact
  match, then widening, then boxing, then varargs. So `add(1, 2)` picks the
  `int` version, and varargs is the last resort — which is why adding a varargs
  overload rarely breaks existing calls.

**Boxing** is Java automatically wrapping a primitive in its matching object
type: an `int` becomes an `Integer`, a `double` a `Double`. Each primitive
has such a **wrapper class**, which is how primitives can go into
collections, since collections only hold objects. Unwrapping again is
**unboxing**. The order above says that, given an `int`, Java would rather
widen it to `long` than box it to `Integer`, which the program at the end of
this lesson shows.

## static against instance

`static` belongs to the class; instance members belong to an object.

```java
static int count;         // one, shared
private double balance;   // one per account
```

(Two field declarations.) Every `Account` object gets its own `balance`,
but there is only one `count`, stored on the class, however many accounts
exist. A static field is reached through the class name, `Account.count`, and
a static method is called the same way, `Math.max(1, 2)`, without creating an
object.

A static method cannot use `this` and cannot touch instance fields, because
there is no instance: `this` means "the object this method was called on",
and a static method was not called on one. The error — "non-static variable
cannot be referenced from a static context" — means exactly that, and it is
what `main` hits when someone tries to use a field from it:

```text
St.java:4: error: non-static variable count cannot be referenced from a static context
    count++;
    ^
```

The fix is either to make the field static, or to create an object
(`new St()`) and use the field through it.

## Constructors

A **constructor** is the code that runs when an object is created with
`new`, to give its fields their starting values. It has the class's name and
no return type, not even `void` (a "constructor" with `void` is an ordinary
method that happens to share the name, and never runs on `new`). If you write
none, Java gives you a no-argument default — **but only if you write none at
all**. Add any constructor and the free one disappears, which breaks
`new Thing()` in a way that reads like a bug:

```text
error: constructor St in class St cannot be applied to given types;
    new St();
    ^
  required: int
  found:    no arguments
```

The class only has `St(int x)` now, so a call with no arguments has nothing
to match. Write the no-argument constructor yourself if you still want one.

A class can have several constructors, overloaded like methods. Chain them
with `this(...)` to keep the logic in one place:

```java
public Account(String owner) {
    this(owner, 0);          // must be the first statement
}
```

`this(owner, 0)` runs the two-argument constructor with a balance of 0, so the
assignments and any checks are written once, there, rather than copied into
every constructor.

`this(...)` calls a sibling constructor; `super(...)` calls the parent's. A
constructor can use one or the other, first, never both. If it uses neither,
Java inserts a call to the parent's no-argument constructor, `super()`, for
you; every object is built from the top of its class hierarchy down.

## Pass by value, always

First, what a variable of an object type actually holds. Take one statement
apart:

```java
Account acc = new Account("ada");
```

- `Account acc` declares a variable named `acc` that can refer to an
  `Account`. On its own, it refers to nothing yet.
- `new Account("ada")` creates a new object, running the constructor with
  `"ada"`, and produces a **reference** to it: in effect, the object's address.
- `=` copies that reference into `acc`.

So `acc` does not contain the account; it contains directions to it. A
primitive variable is different: it contains the value itself, and
assignment copies the value:

```java
public class Copies {
    public static void main(String[] args) {
        int first = 10;
        int second = first;           // copies the number 10
        second = 5;                   // changes only second
        System.out.println(first + " " + second);

        StringBuilder a = new StringBuilder("hi");
        StringBuilder b = a;          // copies the reference: one object, two names
        b.append("!");                // changes the one object
        System.out.println(a + " " + b);
    }
}
```

```output
10 5
hi! hi!
```

Changing `second` left `first` alone, because each holds its own number.
Appending through `b` changed what `a` sees too, because both hold the same
reference. Keep that picture in mind for what follows.

**Pass by value** means a method receives a *copy* of each argument, so
assigning a new value to a parameter cannot affect the caller's variable.
Java passes everything by value. For a primitive, the number itself is
copied. For an object, the variable never held the object, only a reference
to it, so the **reference** is copied, and the method gets a second reference
to the same object:

```java
void rename(Account a) { a.setOwner("x"); }   // caller sees the change
void replace(Account a) { a = new Account(); } // caller sees nothing
```

The first mutates the object both references point at. The second repoints the
local copy and the caller's reference is untouched. Picture two labels tied to
one box: through either label you can change what is in the box, but moving
your own label to another box does nothing to the other label. "Java is pass
by reference" is a persistent myth; the exam tests the difference above
directly.

## Run

```java
public class Methods {
    static String pick(long x) { return "long (widening)"; }
    static String pick(Integer x) { return "Integer (boxing)"; }
    static String pick(int... x) { return "varargs"; }

    static class Account { String owner = "ana"; }
    static void rename(Account a) { a.owner = "x"; }
    static void replace(Account a) { a = new Account(); a.owner = "y"; }

    public static void main(String[] args) {
        System.out.println(pick(5));                   // widening beats boxing
        System.out.println(pick(Integer.valueOf(5)));  // an exact match
        System.out.println(pick());                    // only varargs fits

        Account acc = new Account();
        rename(acc);
        System.out.println(acc.owner);
        replace(acc);
        System.out.println(acc.owner);                 // unchanged by replace
    }
}
```

```output
long (widening)
Integer (boxing)
varargs
x
x
```

`pick(5)` passes an `int`. No `pick(int)` exists, so Java looks for a
widening first and finds `pick(long)`, before it would consider boxing to
`Integer`. `pick(Integer.valueOf(5))` passes an `Integer` already, an exact
match. `pick()` has no arguments, and only varargs accepts none. Then
`rename` changed the shared object, so `acc.owner` is `x`, and `replace`
changed only its own copy of the reference, so `acc.owner` is still `x`.

(`static class Account` is a class declared inside another, a **nested
class**; `static` here means it does not need an instance of `Methods` to
exist. It keeps the example in one file.)

## Your turn

In `Account.java`:

- `private final String owner` and `private double balance`
- `Account(String owner, double balance)` and `Account(String owner)` which
  chains to it with a balance of 0
- `getOwner()`, `getBalance()`
- `deposit(double)` — adds to the balance; `IllegalArgumentException` if the
  amount is not positive (zero or less)
- `withdraw(double)` — subtracts from the balance; `IllegalArgumentException`
  if the amount is not positive or is more than the balance. A rejected
  withdrawal leaves the balance unchanged, so check before you subtract.
- `transferTo(Account other, double amount)` — moves the amount from this
  account to `other`. If the withdrawal is refused, the exception passes
  through and *neither* account changes, which happens naturally if you
  withdraw first and deposit second.

`throw new IllegalArgumentException("amount must be positive");` is how to
reject a value; the Exceptions lesson covers it in full.
