---
title: Optional, and the absence of a value
summary: A type that makes "there might be nothing here" visible in the signature, and the ways of using it that defeat the point.
order: 5
files: [Maybe.java]
run: javac Maybe.java && java Maybe
hints:
  - "`find` returns `Optional.ofNullable(map.get(key))` - ofNullable handles the missing case, where Optional.of(null) would throw."
  - "`nameLength` should map inside the Optional rather than unwrapping: `find(...).map(String::length).orElse(-1)`."
  - "`firstNonBlank` can chain with `or`: `first.or(() -> second)` takes the second only when the first is empty."
  - "`requireValue` throws NoSuchElementException when empty - `orElseThrow()` with no argument does exactly that."
---

`null` carries no information. A method returning `String` might return one,
might return `null`, and the signature does not say which — so every caller
either checks or eventually throws `NullPointerException`.

`Optional<T>` puts that fact in the type.

```java
Optional<String> found = lookup(key);
```

The caller cannot use the value without acknowledging it might not be there,
which is the entire benefit.

## Making one

```java
Optional.of(value)            // throws if value is null
Optional.ofNullable(value)    // empty if value is null
Optional.empty()
```

`of` is for values you know are present; using it on a nullable expression just
moves the `NullPointerException` earlier.

## Using one well

```java
opt.map(String::length)                  // Optional<Integer>
opt.filter(s -> !s.isBlank())
opt.orElse("default")
opt.orElseGet(() -> expensive())         // only evaluated when empty
opt.orElseThrow()                        // NoSuchElementException
opt.ifPresent(System.out::println)
opt.or(() -> otherOptional)
```

`orElse` evaluates its argument **always**, even when the value is present;
`orElseGet` takes a supplier and only calls it when needed. If the default is
costly or has side effects, that difference is a bug rather than a style point.

## Using one badly

```java
if (opt.isPresent()) { use(opt.get()); }
```

This is `null`-checking with extra ceremony and no safety: `get()` on an empty
Optional throws. Prefer `map`, `filter`, `ifPresent` and `orElse` — keep the
value inside the Optional and transform it there.

Two more rules from the API's designers:

- **Do not use `Optional` for fields or parameters.** It is a return type. It
  is not serializable and it adds an allocation for no gain inside an object.
- **Never return `null` from a method that returns `Optional`.** That is the
  worst of both worlds, and it happens more than you would think.

## Your turn

In `Maybe.java`:

- `public static Optional<String> find(Map<String, String> map, String key)`
- `public static int nameLength(Map<String, String> map, String key)` — the
  length, or -1
- `public static Optional<String> firstNonBlank(Optional<String> a, Optional<String> b)`
- `public static String requireValue(Optional<String> value)` — throws
  `NoSuchElementException` when empty
- `public static String orDefault(Optional<String> value, String fallback)`
