---
title: Inheritance, overriding and interfaces
summary: What a subclass may change, why the runtime type decides which method runs, and what an interface can hold now.
order: 6
files: [Shapes.java]
run: javac Shapes.java && java Shapes
hints:
  - "Everything goes in Shapes.java: only ONE class per file may be public, so make Shape, Circle and Square package-private (no modifier) and keep `public class Shapes` as the holder."
  - "`abstract class Shape` declares `public abstract double area();` and a concrete `describe()` that calls it - that call is the polymorphism the test checks."
  - "An overriding method cannot be MORE private than the one it overrides, and @Override makes the compiler check you actually matched the signature."
  - "`Named` is an interface with a `String name()` method; both shapes implement it, and a default method in the interface gives `label()` for free."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **inheritance** | a subclass gets a parent class's fields and methods, and can add or replace them |
| **subclass** / **superclass** (parent) | the class that extends / the class it extends |
| **"is a"** | the relationship inheritance means: a `Circle` is a `Shape` |
| **"has a"** | holding another object in a field instead |
| **composition** | building a class from objects it holds, rather than extending one |
| **abstract class** | cannot be created with `new`; may declare methods without a body |
| **abstract method** | declared without a body; a concrete subclass must supply it |
| **concrete class** | one that can be instantiated: every method has a body |
| **instantiate** | create an object of a class with `new` |
| **single inheritance** | a class has exactly one parent; `Object` if you name none |
| **Javadoc** | Java's official documentation pages, at docs.oracle.com |
| **overriding** | a subclass giving its own version of an inherited method, same name and parameters |
| **subtype** | a class that is a kind of another: `Circle` is a subtype of `Shape` |
| **covariant return** | an override may return a subtype of the original's return type |
| **checked exception** | one the compiler makes you handle or declare (Silver lesson 7) |
| **overload** (by accident) | same name, different parameters: unrelated to the parent's method |
| **polymorphism** | one variable type, many possible behaviours |
| **declared type** vs **actual type** | the variable's type (what you may call) vs the object's class (what runs) |
| **dynamic dispatch** | the JVM picks the method by the object's actual type, at run time |
| **shadowing** a field | declaring a field with the same name in a subclass: two fields, chosen by declared type |
| **interface** | a named set of methods a class promises to provide: a capability |
| **implements** | declares that a class keeps an interface's promise |
| **default method** | an interface method with a body, inherited by every implementing class |
| **lambda** | a short way to write an object with one abstract method: `() -> s` (Gold lesson 3) |
| **instance state** | fields belonging to each object; interfaces cannot have them |
| **cast** | telling the compiler to treat an object as a narrower type |
| **pattern matching** | `instanceof Circle c`: test and cast in one step |
| **scope** | the part of the code where a name can be used |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `javac Shapes.java && java Shapes` | builds and runs this lesson's file |

### Java keywords, classes and methods

| Name | What it does |
|---|---|
| `class Circle extends Shape` | makes `Circle` a subclass of `Shape` |
| `abstract class Shape`, `abstract double area();` | an abstract class and method |
| `@Override` | asks the compiler to check that this really overrides something |
| `interface Named { String name(); }` | declares an interface; `name()` is public and abstract |
| `default String label() { ... }` | a default method |
| `class Shape implements Named` | promises the interface's methods |
| `getClass().getSimpleName()` | the object's actual class name, such as `"Circle"` |
| `Math.PI * r * r` | a circle's area |
| `s instanceof Circle c` | `true` if `s` is a `Circle`, and then `c` is it, typed as `Circle` |
| `(Circle) s` | a cast |
| `Shape[]` | an array that can hold any kind of shape |

### Errors

| Error | Means |
|---|---|
| `Shape is abstract; cannot be instantiated` | `new` on an abstract class |
| `attempting to assign weaker access privileges; was public` | an implementation or override narrowed access |
| `ClassCastException` | a cast to a class the object is not an instance of |
| `method does not override or implement a method from a supertype` | `@Override` on something that overrides nothing |

---

A drawing program has circles, squares and triangles. They share behaviour
(every shape has an area and can describe itself) but each computes its area
differently. **Inheritance** lets the shared parts live in one parent class
while each subclass supplies its own version of what differs. Code can then
handle "any shape" without knowing which one it has, and the right
calculation still runs. This lesson covers the rules for that, and
**interfaces**, Java's way of describing a capability that unrelated classes
can share.

## Extending a class

`class Circle extends Shape` makes `Circle` a **subclass** of `Shape`: it
inherits `Shape`'s fields and methods, and can add its own or replace
inherited ones.

```java
abstract class Shape {
    abstract double area();

    String describe() {
        return getClass().getSimpleName() + " of area " + area();
    }
}

class Circle extends Shape {
    @Override
    double area() { return Math.PI * r * r; }
}
```

(A sketch: `Circle`'s radius field and constructor are left out.)

An **abstract** class cannot be instantiated and may declare methods with no
body. It exists to be extended, and it may still hold state and concrete
methods — which is the difference from an interface that matters most.
`new Shape()` is a compile error (`Shape is abstract; cannot be
instantiated`), which is right: a shape that is no particular shape has no
area. A concrete subclass must give a body to every abstract method it
inherits, or be declared `abstract` itself.

`getClass().getSimpleName()` gives the name of the object's actual class,
such as `"Circle"`, which is how one `describe()` written in the parent
produces the right name for every subclass.

### When not to inherit

Inheritance says "is a": a `Circle` *is a* `Shape`, so it can go anywhere a
`Shape` is expected. A common mistake is to inherit just to reuse code. Say
an `Order` needs a customer's name and address, so someone writes
`class Order extends Customer`. It compiles, and `order.getAddress()` works.
But now an order *is a* customer: it can be passed to any method expecting a
`Customer`, it carries every customer method, including `setAddress`, and
two orders from one customer are two separate customers whose addresses can
drift apart. The honest relationship is "an order *has a* customer":

```java
class Order {
    private final Customer customer;    // has a, not is a
    private final String product;
    ...
}
```

(A sketch.) Holding an object in a field rather than extending its class is
called **composition**. Ask "is X really a kind of Y?" before writing
`extends`; if the answer is "X *has* a Y", use a field.

You can see a class's real place in the hierarchy in its official
documentation, the **Javadoc**: the page for `String` begins with
`java.lang.Object` above `java.lang.String`, and lists every interface it
implements. The pages are at docs.oracle.com, and reading them is a habit
worth starting now.

Java has **single inheritance**: one `extends`, any number of `implements`. A
class has exactly one parent (`Object`, if you name none), which keeps the
question "which version of this method runs?" simple to answer.

## Overriding rules

**Overriding** means a subclass providing its own version of a method it
inherited. An override must have the same name and parameters, and:

- the return type must be the same or a **subtype** (covariant returns): if
  the parent's method returns `Shape`, the child's may return `Circle`
- access may widen but never narrow — `protected` can become `public`, not
  `private`
- it may not throw broader *checked* exceptions than the original (checked
  exceptions are explained in the Exceptions lesson)

All three rules come from one idea: code written against the parent must
keep working when handed a child. If the parent promises a public method,
the child cannot make it private; if the parent promises a `Shape`, getting a
`Circle` is fine, because a circle is a shape.

`@Override` is optional and worth always writing: it turns "I thought I was
overriding" into a compile error. A method that differs in parameters is an
**overload**, quietly unrelated to the parent's, and that is one of the
exam's favourite illusions.

## Polymorphism

```java
Shape s = new Circle(2);
s.area();          // Circle's area - decided at RUNTIME by the object's type
```

A variable of a parent type can hold any subclass object, because a circle
*is a* shape. **Polymorphism** ("many forms") is the result: one variable
type, many possible behaviours.

The variable's declared type decides what you may *call*; the object's actual
type decides what *runs*. The first is checked by the compiler, which only
knows the declared type; the second is decided by the JVM while the program
runs, which knows the real object. That is **dynamic dispatch**, and it is why
`describe()` in the parent can call `area()` and get the child's version.

Fields do not work this way. Fields are resolved by the declared type, at
compile time, so declaring a field with the same name in a subclass
(**shadowing** it) gives you two fields and a confusing bug: which one you
see depends on the variable's type. The program below shows it.

## Interfaces

An **interface** is a named set of methods that a class promises to
provide: a capability, such as "can be named" or "can be compared", rather
than a kind of thing. A class declares the promise with `implements`, and any
number of unrelated classes can make it. Code can then accept "anything
`Named`" without caring what else the object is.

```java
interface Named {
    String name();                                   // abstract, public

    default String label() { return "<" + name() + ">"; }
    static Named of(String s) { return () -> s; }
}
```

Methods declared in an interface without a body are automatically `public`
and `abstract`. That has a consequence the compiler enforces: the class's
version must be `public` too, since an implementation may not narrow access.
Writing `String name() { ... }` in the class, with no modifier, fails with
`name() in Wk cannot implement name() in N` followed by
`attempting to assign weaker access privileges; was public`.

`() -> s` in the `of` method is a **lambda**, a short way of writing an
object that implements an interface with one abstract method (the Gold
section covers them). Here it is a `Named` whose `name()` returns `s`.

Since Java 8 an interface may have `default` methods (inherited, overridable)
and `static` ones. Since Java 9, `private` helpers too. What it still cannot
have is instance state — no fields except `public static final` constants.
A `default` method is the interesting one: it gives every implementing class
working behaviour for free, built on the abstract methods, so `label()` works
on anything that provides `name()`.

A class implementing two interfaces with the same default method must override
it, which is how Java allows multiple inheritance of *behaviour* without the
ambiguity of multiple inheritance of *state*.

## instanceof

```java
if (s instanceof Circle c) {    // pattern matching, Java 16+
    ...c.radius()...
}
```

`instanceof` asks "is this object an instance of that class, or of a
subclass of it?". The old way to use a `Shape` as a `Circle` was to test and
then **cast**, telling the compiler to treat it as the narrower type; the
pattern form does both:

```java
// before Java 16: test, then cast, repeating the type
if (s instanceof Circle) {
    Circle c = (Circle) s;
    ...c.radius()...
}
```

The pattern form tests and casts in one step, and `c` is only in scope where
the test succeeded — which removes the cast that used to follow every
`instanceof` and the `ClassCastException` when someone got it wrong. (A
`ClassCastException` is the run-time error for casting an object to a class
it is not an instance of.)

## Run

```java
public class Dispatch {
    static class Parent {
        String name = "parent-field";
        String who() { return "parent"; }
        String greet(Object o) { return "parent greet"; }
    }

    static class Child extends Parent {
        String name = "child-field";
        @Override String who() { return "child"; }
        String greet(String s) { return "child greet"; }   // an overload, not an override
    }

    interface Named {
        String name();
        default String label() { return "<" + name() + ">"; }
    }

    public static void main(String[] args) {
        Parent p = new Child();
        System.out.println(p.who());        // methods: the object's type
        System.out.println(p.name);         // fields: the variable's type
        System.out.println(p.greet("hi"));  // Parent has only greet(Object)

        Named n = () -> "ana";
        System.out.println(n.label());

        Object o = p;
        if (o instanceof Child c) System.out.println("a Child, field " + c.name);
    }
}
```

```output
child
parent-field
parent greet
<ana>
a Child, field child-field
```

Line by line, with `p` declared as `Parent` but holding a `Child`:

- `p.who()` runs `Child`'s override: methods follow the object.
- `p.name` reads `Parent`'s field: fields follow the variable's type.
- `p.greet("hi")` runs `Parent`'s `greet(Object)`. The compiler chose the
  method from `Parent`, the declared type, and `Parent` has no
  `greet(String)`. `Child`'s `greet(String)` has different parameters, so it
  is an overload, not an override, and dispatch never considers it. With
  `@Override` on it, the compiler would have said so.
- `n.label()` runs the default method, which calls the lambda's `name()`.
- Through `c`, typed as `Child`, the field read is `Child`'s.

## Your turn

In `Shapes.java` (all in one file: only `Shapes` is public, the others have no
access modifier):

- `interface Named` with `String name()` and a `default String label()`
  returning `"<"` + `name()` + `">"`, such as `"<circle>"`
- `abstract class Shape implements Named` with `abstract double area()` and
  `String describe()` returning `"<name> area=<area>"`, such as
  `"square area=9.0"`. Because `Shape` implements `Named`, `describe()` can
  call `name()`; an abstract class does not have to provide the body itself,
  and each subclass does.
- `class Circle extends Shape implements Named` — constructor takes the radius,
  `name()` returns `"circle"`, area is `Math.PI * r * r`
- `class Square extends Shape implements Named` — constructor takes the side,
  `name()` returns `"square"`, area is side times side
- `public class Shapes` with a `main`

`name()` comes from an interface, so the implementations must be declared
`public`. A test also checks that `Shape` really is abstract, and that a
`Shape[]` can hold both kinds.
