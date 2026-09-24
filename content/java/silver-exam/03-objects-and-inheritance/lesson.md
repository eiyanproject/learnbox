---
title: "Paper 3: objects, inheritance and dispatch"
summary: Constructor chaining, what overriding really requires, and the difference between the type you declared and the object you made.
order: 3
files: [Paper3.java]
run: javac Paper3.java && java Paper3
hints:
  - "Keep one public class: `public class Paper3` plus package-private Animal, Dog and Cat in the same file."
  - "`Animal.speak()` returns \"...\"; Dog and Cat override it. `describe()` on Animal calls speak(), and the override is what runs - that is the dispatch being tested."
  - "`Animal` has a no-argument constructor chaining to `Animal(String name)` with \"unnamed\" via `this(\"unnamed\")`."
  - "`soundOf(Animal a)` takes the PARENT type and returns a.speak() - the caller passes a Dog, and Dog's version runs."
---

The third paper is the object model: constructors, overriding, and which method
actually runs.

## Worth re-reading

- **A constructor is not inherited.** A subclass must define its own, and its
  first action is always a call to a parent constructor — `super(...)`
  explicitly, or the no-argument one implicitly. If the parent has no
  no-argument constructor and you do not call `super(...)`, it does not
  compile.
- **`this(...)` and `super(...)` must be first**, and you may use only one.
- **Overriding needs the same signature.** Different parameters make an
  overload, which is a different method that quietly does not override
  anything. `@Override` turns that mistake into an error.
- **Access may widen, never narrow**, and return types may be covariant.
- **Methods dispatch on the runtime type; fields do not.** A field with the
  same name in a subclass shadows rather than overrides, and which one you get
  depends on the declared type of the variable.
- **`static` methods are hidden, not overridden.** Redeclaring one in a
  subclass looks like overriding and follows the *declared* type instead.

## The one that decides most questions

```java
Animal a = new Dog();
a.speak();       // Dog's speak
```

The declared type `Animal` decides what you are **allowed to call**. The actual
object decides **which implementation runs**. Nearly every inheritance question
on the exam is this sentence in disguise.

## Your turn

In `Paper3.java`:

- `class Animal` with a `name` field, `Animal(String name)`, a no-argument
  constructor chaining to it with `"unnamed"`, `getName()`, `String speak()`
  returning `"..."`, and `String describe()` returning `"<name> says <speak>"`
- `class Dog extends Animal` — `speak()` returns `"woof"`, constructor takes a
  name
- `class Cat extends Animal` — `speak()` returns `"meow"`
- `public class Paper3` with
  `public static String soundOf(Animal a)` returning `a.speak()`
