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

## Extending a class

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

An **abstract** class cannot be instantiated and may declare methods with no
body. It exists to be extended, and it may still hold state and concrete
methods — which is the difference from an interface that matters most.

Java has **single inheritance**: one `extends`, any number of `implements`.

## Overriding rules

An override must have the same name and parameters, and:

- the return type must be the same or a **subtype** (covariant returns)
- access may widen but never narrow — `protected` can become `public`, not
  `private`
- it may not throw broader *checked* exceptions than the original

`@Override` is optional and worth always writing: it turns "I thought I was
overriding" into a compile error. A method that differs in parameters is an
**overload**, quietly unrelated to the parent's, and that is one of the
exam's favourite illusions.

## Polymorphism

```java
Shape s = new Circle(2);
s.area();          // Circle's area - decided at RUNTIME by the object's type
```

The variable's declared type decides what you may *call*; the object's actual
type decides what *runs*. That is dynamic dispatch, and it is why `describe()`
in the parent can call `area()` and get the child's version.

Fields do not work this way. Fields are resolved by the declared type, so
shadowing a field in a subclass gives you two fields and a confusing bug.

## Interfaces

```java
interface Named {
    String name();                                   // abstract, public

    default String label() { return "<" + name() + ">"; }
    static Named of(String s) { return () -> s; }
}
```

Since Java 8 an interface may have `default` methods (inherited, overridable)
and `static` ones. Since Java 9, `private` helpers too. What it still cannot
have is instance state — no fields except `public static final` constants.

A class implementing two interfaces with the same default method must override
it, which is how Java allows multiple inheritance of *behaviour* without the
ambiguity of multiple inheritance of *state*.

## instanceof

```java
if (s instanceof Circle c) {    // pattern matching, Java 16+
    ...c.radius()...
}
```

The pattern form tests and casts in one step, and `c` is only in scope where
the test succeeded — which removes the cast that used to follow every
`instanceof` and the `ClassCastException` when someone got it wrong.

## Your turn

In `Shapes.java`:

- `interface Named` with `String name()` and a `default String label()`
  returning `"<name>"`
- `abstract class Shape` with `abstract double area()` and
  `String describe()` returning `"<name> area=<area>"` via the interface
- `class Circle extends Shape implements Named` — constructor takes the radius,
  `name()` returns `"circle"`, area is `Math.PI * r * r`
- `class Square extends Shape implements Named` — `name()` returns `"square"`
- `public class Shapes` with a `main`
