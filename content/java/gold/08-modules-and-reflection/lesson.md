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

## Modules

Java 9 added modules on top of packages. A module declares what it exposes and
what it needs:

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

An annotation is metadata attached to code. Declaring one:

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

## Reflection

```java
Class<?> type = obj.getClass();
type.getDeclaredMethods();
method.isAnnotationPresent(Marked.class);
method.invoke(obj, args);
```

Reflection is how JUnit finds your `@Test` methods, how Spring wires beans, and
how serialisers read fields. It costs performance, discards compile-time
safety, and is the right tool exactly when the thing you are writing must work
on classes it has never seen.

`getDeclaredMethods` returns this class's methods including private ones;
`getMethods` returns public ones including inherited. Neither promises an
order, so code that depends on one is flaky.

## Your turn

In `Meta.java`:

- `@interface Marked` with a `String value() default ""`, retained at runtime,
  targeting methods
- a class `Sample` with three methods, two of them `@Marked` (one with a value)
- `public static List<String> methodsWith(Class<?> type)` — names of annotated
  methods, sorted
- `public static String describeAnnotation(Class<?> type, String methodName)` —
  the annotation's value, or `"none"`
