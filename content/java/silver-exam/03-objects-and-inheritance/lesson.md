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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **constructor** | sets up a new object; constructors are **not inherited** |
| **`this(...)`** / **`super(...)`** | call another constructor of this class / of the parent; must be first |
| **implicit `super()`** | inserted for you when a constructor calls neither |
| **overriding** | same signature in a subclass; needs the same name and parameters |
| **widen access** | an override may be more public, never less |
| **`@Override`** | asks the compiler to check that you really override |
| **dynamic dispatch** | methods run by the object's actual type, at run time |
| **fields by declared type** | fields are chosen by the variable's type, not the object's |
| **hiding** | a `static` method with the same signature in a subclass hides, not overrides |
| **declared type** vs **runtime type** | what you are allowed to call vs which implementation runs |
| **package-private** | no access modifier: one file can hold several such classes, but only one public |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `javac Paper3.java && java Paper3` | builds and runs this paper's file |

### Java names

| Name | What it does |
|---|---|
| `class Dog extends Animal` | `Dog` is a subclass of `Animal` |
| `Animal(String name)`, `Animal()` | two constructors; the second can chain with `this("unnamed")` |
| `Dog(String name) { super(name); }` | passes the name to the parent's constructor |
| `String speak()` | overridden in each subclass |
| `"<name> says <speak>"` | built in the parent, using the child's `speak()` |
| `Animal a = new Dog("rex");` | a parent-type variable holding a child object |

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

One program, four of the rules. Treat it as a practice question: cover the output, write down what you expect each line to be, then compare.

```java
public class Hiding {
    static class Animal {
        String name = "animal";
        Animal() { System.out.println("Animal()"); }
        static String kind() { return "Animal.kind"; }
        String speak() { return "..."; }
    }

    static class Dog extends Animal {
        String name = "dog";
        Dog() { System.out.println("Dog()"); }          // super() runs first
        static String kind() { return "Dog.kind"; }     // hides, does not override
        @Override String speak() { return "Woof"; }
    }

    public static void main(String[] args) {
        Animal a = new Dog();
        System.out.println(a.speak() + " " + a.name + " " + a.kind());
    }
}
```

```output
Animal()
Dog()
Woof animal Animal.kind
```

Following it through. `new Dog()` runs `Dog`'s constructor, whose hidden
first line is `super()`, so `Animal()` prints before `Dog()`: objects are
built from the parent down. Then, with `a` declared as `Animal`:

- `a.speak()` is an instance method, overridden in `Dog`, so the object's
  type decides: `Woof`.
- `a.name` is a field, so the declared type decides: `Animal`'s `name`.
- `a.kind()` is a static method. It belongs to a class, not an object, so it
  is chosen by the declared type at compile time: `Animal.kind`. Calling a
  static method through a variable, as here, is legal but misleading (the
  compiler warns about it); write `Animal.kind()` in real code.

## Your turn

In `Paper3.java`:

All in the one file: `public class Paper3`, plus the other three classes with
no access modifier.

- `class Animal` with a `name` field, `Animal(String name)`, a no-argument
  constructor chaining to it with `"unnamed"` (so `new Animal().getName()` is
  `"unnamed"`), `getName()`, `String speak()` returning `"..."`, and
  `String describe()` returning `"<name> says <speak>"`, built by calling
  `speak()`, so that `new Dog("rex").describe()` is `"rex says woof"`
- `class Dog extends Animal` — constructor takes a name and passes it up with
  `super(name)`; `speak()` returns `"woof"`
- `class Cat extends Animal` — the same, with `speak()` returning `"meow"`
- `public class Paper3` with
  `public static String soundOf(Animal a)` returning `a.speak()`
