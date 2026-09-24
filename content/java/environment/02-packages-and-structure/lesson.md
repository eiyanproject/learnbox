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

A package is a namespace, and Java ties it to the filesystem: `com.example.app`
lives in `com/example/app/`. That mapping is not a convention the tooling
happens to follow — the compiler and the launcher both depend on it.

```java
package com.example.util;     // must be the first statement in the file

import java.util.List;        // one class
import java.util.*;           // everything in that package, but NOT subpackages
```

Two things the exam likes:

- **`import java.util.*` does not import `java.util.concurrent`.** The star is
  one level only; subpackages are separate packages.
- **`java.lang` is imported automatically.** `String`, `System`, `Integer`,
  `Math` and `Object` need no import, which is why they seem special.

An import never *includes* code. It is a shorthand so you can write `List`
instead of `java.util.List`; the class is found on the classpath either way.

## Access levels

| Modifier | Same class | Same package | Subclass | Anywhere |
|---|---|---|---|---|
| `private` | yes | no | no | no |
| *(none)* — package-private | yes | yes | no | no |
| `protected` | yes | yes | yes | no |
| `public` | yes | yes | yes | yes |

The default with no modifier is **package-private**, not public. That catches
people who expect "no modifier" to mean "open".

`protected` is the odd one: it means package-private **plus** subclasses, even
subclasses in other packages. It is not "more private than package-private",
which the layout of the table above makes clear.

## static and final

- `static` belongs to the class, not an instance. One copy, shared.
- `final` cannot be reassigned after initialisation.
- `static final` is a constant — conventionally `UPPER_SNAKE_CASE`.

`final` on a reference stops *reassignment*, not mutation: a `final List` can
still have things added to it. That distinction is examined often.

## Your turn

In `Temperature.java`, a class demonstrating encapsulation:

- a `private double celsius` field
- a constructor taking the celsius value
- `public double getCelsius()` and `public void setCelsius(double)`
- `public double toFahrenheit()` returning `celsius * 9.0 / 5.0 + 32`
- `public static final double ABSOLUTE_ZERO = -273.15;`
- a `main` that prints something using them
