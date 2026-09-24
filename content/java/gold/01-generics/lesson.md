---
title: Generics and wildcards
summary: Type parameters, erasure and what it costs you, and the PECS rule that decides which wildcard to write.
order: 1
files: [Boxes.java]
run: javac Boxes.java && java Boxes
hints:
  - "`Box<T>` holds one value: a constructor, `get()`, and `set(T)`. The type parameter goes after the class name."
  - "`sumAll(List<? extends Number> values)` - `? extends` lets you READ Numbers out of a list of Integer or Double. You cannot add to it."
  - "`addNumbers(List<? super Integer> target)` - `? super` lets you WRITE Integers into a list of Integer, Number or Object."
  - "`firstOrDefault` is a generic METHOD: the `<T>` goes before the return type, as in `public static <T> T firstOrDefault(List<T> list, T fallback)`."
---

Generics move type errors from runtime to compile time. Before them, every
collection held `Object` and every read needed a cast that might fail.

```java
class Box<T> {
    private T value;
    T get() { return value; }
    void set(T value) { this.value = value; }
}
```

`T` is a placeholder filled in at each use: `Box<String>`, `Box<Integer>`.

## Erasure, and what it costs

Generics exist only at compile time. The compiler checks your types, then
**erases** them — `Box<String>` and `Box<Integer>` are the same class at
runtime. Three consequences the exam asks about:

- `new T()` is impossible; there is no `T` at runtime.
- `new T[10]` is impossible for the same reason.
- `list instanceof List<String>` does not compile — only `List<?>` does.

Erasure is why generics interoperate with pre-generic code, and why they cannot
do everything a reified system could.

## Wildcards, and PECS

A `List<Integer>` is **not** a `List<Number>`, even though an `Integer` is a
`Number`. If it were, you could add a `Double` to it through the wider
reference and break the original. Wildcards restore the flexibility safely:

```java
double sum(List<? extends Number> values)   // read Numbers out
void fill(List<? super Integer> target)     // write Integers in
```

**PECS — Producer Extends, Consumer Super.** If the parameter *produces* values
for you to read, use `extends`. If it *consumes* values you put in, use
`super`.

The restriction follows from the same argument: with `? extends Number` the
list might be `List<Double>`, so adding an `Integer` must be refused — you can
read, not write. With `? super Integer` it might be `List<Object>`, so anything
you read is only guaranteed to be an `Object`.

## Bounded type parameters

```java
<T extends Comparable<T>> T max(List<T> list)
```

The bound says what you may *do* with `T` — here, call `compareTo`. Without it
`T` is only an `Object`. A parameter may have several bounds with `&`.

## Your turn

In `Boxes.java`:

- `public static class Box<T>` with a constructor, `get()` and `set(T)`
- `public static double sumAll(List<? extends Number> values)`
- `public static void addNumbers(List<? super Integer> target, int count)` —
  adds 1..count
- `public static <T> T firstOrDefault(List<T> list, T fallback)`
- `public static <T extends Comparable<T>> T largest(List<T> list)`
