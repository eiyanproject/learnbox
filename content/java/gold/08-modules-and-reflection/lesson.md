---
title: Modules, annotations and reflection
summary: What module-info declares, why annotations need a retention policy to survive, and the reflection the frameworks are built on.
order: 8
files: [Meta.java]
run: javac Meta.java && java Meta
hints:
  - "`@Retention(RetentionPolicy.RUNTIME)` is the whole lesson: without it the annotation is discarded and reflection cannot see it. The default is CLASS, which is not enough."
  - "`@Target(ElementType.METHOD)` restricts where it may be written; the test checks a method annotation is found."
  - "`methodsWith` iterates `type.getDeclaredMethods()` and keeps those where `m.isAnnotationPresent(Marked.class)`. Sort the names so the result is deterministic - reflection does not promise an order."
  - "`describeAnnotation` reads an element from the annotation instance: `m.getAnnotation(Marked.class).value()`."
---

This lesson covers three features used far more by frameworks than by
application code, which is exactly why they are worth understanding: they
explain what JUnit, Spring and the serialisation libraries are doing to your
classes. **Modules** control which packages other code may see,
**annotations** attach information to code, and **reflection** lets a program
inspect and call classes it has never seen before.

## Modules

Java 9 added modules on top of packages. A **module** is a named group of
packages, described by a file called `module-info.java` at the root of the
source tree. A module declares what it exposes and what it needs:

```java
module com.example.app {
    requires java.net.http;          // what I depend on
    exports com.example.api;         // what others may use
    opens com.example.model;         // what reflection may reach
}
```

Three ideas worth having:

- **Strong encapsulation.** A public class in a package that is not `exports`ed
  is unreachable from outside the module. Before modules, `public` meant public
  to the world.
- **`exports` is compile and run time; `opens` is reflection.** Frameworks that
  inspect your classes need `opens`, which is why adding modules to an old
  project breaks Jackson or Hibernate until you open the right packages.
- **The classpath still works.** Code without `module-info.java` lands in the
  *unnamed module*, which reads everything — which is why you can ignore
  modules entirely and most people do.

## Annotations

An **annotation** is metadata attached to code: a note that does nothing by
itself, but that tools and frameworks can look for. You have written several
already: `@Override` (for the compiler), `@Test` (for JUnit),
`@FunctionalInterface`. An annotation is declared with `@interface`, and its
**elements** look like methods with no body, optionally with a `default`.
Declaring one:

```java
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
@interface Marked {
    String value() default "";
}
```

The **retention policy** decides how long it survives:

| | |
|---|---|
| `SOURCE` | discarded by the compiler — `@Override`, `@SuppressWarnings` |
| `CLASS` | in the class file, not loaded — **the default** |
| `RUNTIME` | visible to reflection |

That default is the catch. An annotation you intend to read at runtime and
forget to mark `RUNTIME` simply is not there, and nothing warns you.

`@Retention` and `@Target` are themselves annotations, applied to the
annotation's declaration (annotations about annotations are called
**meta-annotations**). `@Target(ElementType.METHOD)` restricts where `Marked`
may be written; putting it on a class would then be a compile error.

Using it: `@Marked("first")` sets `value` to `"first"`. An element called
`value` is special, in that it can be given without its name; any other
element is written by name, `@Marked(label = "x")`. `@Marked` alone uses the
default, here `""`.

## Reflection

**Reflection** means a program examining its own structure while it runs:
asking a class for its methods and fields, reading their annotations, and
calling them, all by name rather than through code written in advance.

```java
Class<?> type = obj.getClass();
type.getDeclaredMethods();
method.isAnnotationPresent(Marked.class);
method.invoke(obj, args);
```

(Calls in sequence.) Every class is represented at run time by a `Class`
object, from `obj.getClass()` or `SomeClass.class`; `Class<?>` means "a class
object for some unknown class". Its `getDeclaredMethods()` returns `Method`
objects, which can report their name (`getName()`), their annotations
(`isAnnotationPresent`, `getAnnotation`), and be called with `invoke`.
`getDeclaredMethod("one")` looks one up by name, and throws
`NoSuchMethodException` if there is none.

Reflection is how JUnit finds your `@Test` methods, how Spring wires beans, and
how serialisers read fields. It costs performance, discards compile-time
safety, and is the right tool exactly when the thing you are writing must work
on classes it has never seen.

`getDeclaredMethods` returns this class's methods including private ones;
`getMethods` returns public ones including inherited. Neither promises an
order, so code that depends on one is flaky.

## Run

```java
import java.lang.annotation.*;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class Reflect {
    @Retention(RetentionPolicy.RUNTIME) @Target(ElementType.METHOD) @interface Kept {}
    @Target(ElementType.METHOD) @interface Dropped {}       // CLASS retention, the default

    static class Job {
        @Kept public void a() {}
        @Dropped public void b() {}
        private void c() {}
    }

    public static void main(String[] args) {
        List<String> seen = new ArrayList<>();
        for (Method m : Job.class.getDeclaredMethods()) {
            String name = m.getName();
            if (m.isAnnotationPresent(Kept.class)) name += "+Kept";
            if (m.isAnnotationPresent(Dropped.class)) name += "+Dropped";
            seen.add(name);
        }
        Collections.sort(seen);              // no promised order: sort first
        System.out.println(seen);
    }
}
```

```output
[a+Kept, b, c]
```

`b` carries `@Dropped` in the source, and reflection cannot see it. `@Kept`
has `RUNTIME` retention and is found on `a`; `@Dropped` has the default
`CLASS` retention, so it was stored in the class file but never loaded, and
`isAnnotationPresent` says `false`. The private `c` is listed, because
`getDeclaredMethods` includes private methods.

## Your turn

In `Meta.java`:

Declare these inside the `Meta` class (the tests refer to `Meta.Marked` and
`Meta.Sample`):

- `@interface Marked` with a `String value() default ""`, retained at runtime,
  targeting methods
- `public static class Sample` with three public methods: `one()` marked
  `@Marked("first")`, `two()` marked `@Marked` with no value, and `three()`
  with no annotation
- `public static List<String> methodsWith(Class<?> type)` — the names of the
  type's declared methods that carry `@Marked`, sorted alphabetically (for
  `Sample`, `["one", "two"]`); an empty list for a class with none, such as
  `String`
- `public static String describeAnnotation(Class<?> type, String methodName)` —
  the annotation's value for that method, or `"none"` when the method has no
  `@Marked`, when its value is the empty default, or when there is no method
  of that name at all (catch `NoSuchMethodException`)
