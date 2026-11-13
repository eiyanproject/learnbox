---
title: Packages, imports and structure
summary: How a package name becomes a directory, what import really does, and the access levels that decide what is visible.
order: 2
files: [Temperature.java]
run: javac Temperature.java && java Temperature
hints:
  - "This lesson uses the default package, so no `package` line is needed - the topic is what the modifiers do, not directory layout."
  - "`private` fields plus public methods is the encapsulation the exam asks about: the field cannot be reached from outside, the method can."
  - "`toFahrenheit` is `celsius * 9.0 / 5.0 + 32`. Use 9.0 rather than 9, or integer division truncates before the addition."
  - "A `static final` constant is written in capitals by convention: `public static final double ABSOLUTE_ZERO = -273.15;`"
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **package** | a named group of classes, such as `java.util`; part of each class's full name |
| **namespace** | a space in which names must be unique; packages let two `List` classes exist |
| **reversed domain name** | the package naming convention: `example.com` gives `com.example` |
| **fully qualified name** | a class's name with its package: `java.util.List`, `com.example.app.Main` |
| **default package** | the unnamed package of a file with no `package` line |
| **import** | a shorthand that lets you write `List` instead of `java.util.List`; it includes no code |
| **star import** | `import java.util.*`: every class in that one package, but not its subpackages |
| **subpackage** | a package whose name continues another's, such as `java.util.concurrent`; it is a separate package |
| **`java.lang`** | the package imported automatically: `String`, `System`, `Integer`, `Math`, `Object` |
| **symbol** | a name the compiler must resolve: a class, variable or method |
| **member** | a field, method or constructor of a class |
| **field** | a variable that belongs to a class or object |
| **constructor** | the special method that sets up a new object |
| **access modifier** | `private`, `protected`, `public`, or none: who may use a member |
| **access level** | the resulting visibility of a member |
| **`private`** | the same class only |
| **package-private** | no modifier: the same package only (not public!) |
| **`protected`** | package-private plus subclasses, even in other packages |
| **subclass** | a class that extends another (Silver lesson 6) |
| **encapsulation** | keeping fields private and giving outside code methods instead |
| **getter** / **setter** | a method that reads / changes a private field: `getCelsius`, `setCelsius` |
| **instance** | one object made from a class |
| **`static`** | belongs to the class, one shared copy, usable without an object |
| **`final`** | cannot be reassigned after it is first set |
| **constant** | a `static final` value, named in `UPPER_SNAKE_CASE` |
| **reassignment** vs **mutation** | pointing a variable at a new object vs changing the object it points at; `final` stops only the first |
| **integer division** | dividing two whole numbers throws the fraction away: `9 / 5` is 1 |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `javac -d out src/com/example/app/Main.java ...` | compiles, writing `.class` files under `out/` in package folders |
| `java -cp out com.example.app.Main` | runs a class by its fully qualified name, looking in `out/` |
| `javac Temperature.java && java Temperature` | builds and runs this lesson's file |

### Java keywords, classes and methods

| Name | What it does |
|---|---|
| `package com.example.util;` | puts the file's classes in that package; must be the first statement |
| `import java.util.List;` | lets you write `List` for `java.util.List` |
| `import java.util.*;` | every class in `java.util`, but not in `java.util.concurrent` |
| `private double celsius;` | a private field holding a decimal number |
| `double` | the type for decimal numbers |
| `public double getCelsius()` | a getter |
| `public void setCelsius(double c)` | a setter |
| `public static final double ABSOLUTE_ZERO = -273.15;` | a public constant |
| `Math.max(1, 2)`, `Math.PI` | a static method and a constant of the class `Math` |
| `Integer.MAX_VALUE` | the largest `int` |
| `final List<String> names = new ArrayList<>();` | a final variable holding a list that can still change |
| `names.add("Ada")` | adds to the list |
| `ConcurrentHashMap` | a map from `java.util.concurrent`, used to show the star-import trap |

### Errors

| Error | Means |
|---|---|
| `error: cannot find symbol` | the compiler does not know that name: a missing import or a typo |
| `error: celsius has private access in T` | code outside the class tried to use a private member |
| `error: cannot assign a value to final variable names` | a `final` variable was reassigned |

---

A real program has hundreds of classes, and the standard library has
thousands more. Two problems follow. Names collide: your `List` and Java's
`List` cannot both just be called `List`. And not every class or field should
be usable from everywhere: some are internal details that other code must not
depend on. **Packages** solve the first problem, and **access modifiers** the
second.

## Packages and directories

A **package** is a namespace: a named group of classes, whose full names
include the package. The standard library's `List` is really
`java.util.List`, and yours could be `com.example.app.List`, with no clash.
Package names are conventionally your organisation's domain name reversed,
which keeps them unique worldwide.

Java ties packages to the filesystem: `com.example.app` lives in
`com/example/app/`. That mapping is not a convention the tooling happens to
follow — the compiler and the launcher both depend on it to find a class from
its name:

```text
src/
  com/example/app/Main.java        package com.example.app;
  com/example/util/Strings.java    package com.example.util;
```

```bash
javac -d out src/com/example/app/Main.java src/com/example/util/Strings.java
java -cp out com.example.app.Main
```

`-d out` tells `javac` to write the `.class` files under `out/`, in the same
directory structure. To run, you give the launcher the class's **fully
qualified name**, package included, and it turns the dots back into
directories to find `out/com/example/app/Main.class`.

The declaration and imports go at the top of the file:

```java
package com.example.util;     // must be the first statement in the file

import java.util.List;        // one class
import java.util.*;           // everything in that package, but NOT subpackages
```

(A fragment: the start of a file, before its class.) A file with no `package`
line is in the **default package**, the unnamed one. That is fine for small
programs like this course's exercises, but real code always declares a
package.

Two things the exam likes:

- **`import java.util.*` does not import `java.util.concurrent`.** The star is
  one level only; subpackages are separate packages, despite the dotted
  names. Using `ConcurrentHashMap` with only that import fails to compile:

  ```text
  Star.java:3: error: cannot find symbol
    symbol:   class ConcurrentHashMap
    location: class Star
  ```

- **`java.lang` is imported automatically.** `String`, `System`, `Integer`,
  `Math` and `Object` need no import, which is why they seem special.

An import never *includes* code, the way `#include` does in C. It is a
shorthand so you can write `List` instead of `java.util.List`; the class is
found on the classpath either way, and a fully qualified name works with no
import at all. "cannot find symbol" is the compiler's message for a name it
does not know, whether from a missing import or a typo.

## Access levels

Every class, field, method and constructor has an **access level** that
decides which other code may use it:

| Modifier | Same class | Same package | Subclass | Anywhere |
|---|---|---|---|---|
| `private` | yes | no | no | no |
| *(none)* — package-private | yes | yes | no | no |
| `protected` | yes | yes | yes | no |
| `public` | yes | yes | yes | yes |

Read each row as "who can see a member declared like this". Each level, from
top to bottom, allows everything the one above it does, and more.

The default with no modifier is **package-private**, not public. That catches
people who expect "no modifier" to mean "open".

`protected` is the odd one: it means package-private **plus** subclasses, even
subclasses in other packages. It is not "more private than package-private",
which the layout of the table above makes clear.

Access is checked by the compiler, so breaking it is a compile-time error,
not something that fails while running:

```text
$ javac Peek.java
Peek.java:3: error: celsius has private access in T
    System.out.println(t.celsius);
                        ^
1 error
```

### Encapsulation

Making fields `private` and giving outside code methods instead is called
**encapsulation**. Callers use `getCelsius()` and `setCelsius(...)` rather than
the field itself, so the class stays in control of its own data: a setter can
later reject impossible values, or the class can change how it stores the
temperature, without any caller having to change. Methods named `getX` and
`setX` are called **getters** and **setters**.

## static and final

- `static` belongs to the class, not an instance. One copy, shared by every
  object, and usable without creating one: `Math.max(1, 2)` calls a static
  method on the class `Math` itself.
- `final` cannot be reassigned after initialisation.
- `static final` is a constant — conventionally `UPPER_SNAKE_CASE`, such as
  `Math.PI` or `Integer.MAX_VALUE`.

`final` on a reference stops *reassignment*, not mutation: a `final List` can
still have things added to it. The variable always points at the same list,
but the list itself can change. That distinction is examined often:

```java
import java.util.ArrayList;
import java.util.List;

public class FinalList {
    public static void main(String[] args) {
        final List<String> names = new ArrayList<>();
        names.add("Ada");            // fine: changes the list
        names.add("Bo");
        System.out.println(names);
        // names = new ArrayList<>();   would not compile: reassigns a final
    }
}
```

```output
[Ada, Bo]
```

Uncommenting the last line gives
`error: cannot assign a value to final variable names`, at compile time.

## Your turn

In `Temperature.java` (in the default package, so no `package` line), a class
demonstrating encapsulation:

- a `private double celsius` field (a test checks that it is private)
- a constructor taking the celsius value
- `public double getCelsius()` and `public void setCelsius(double)`
- `public double toFahrenheit()` returning `celsius * 9.0 / 5.0 + 32`:
  0 °C is 32.0, 100 °C is 212.0, and 37 °C is 98.6. Write `9.0`, not `9`: in
  Java, dividing one whole number by another throws away the fraction, the
  first lesson of the Silver section.
- `public static final double ABSOLUTE_ZERO = -273.15;`
- a `main` that prints something using them; what it prints is up to you
