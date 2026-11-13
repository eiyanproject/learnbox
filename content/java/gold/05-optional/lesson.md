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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **`null`** | "no object"; it carries no information and causes `NullPointerException` |
| **null reference** | a variable that refers to nothing |
| **`Optional<T>`** | a small container holding one `T` or nothing |
| **present** / **empty** | the Optional holds a value / holds nothing |
| **in the type** | the signature itself says "there may be no answer", so callers must handle it |
| **bridge** | `ofNullable`: turns code that returns `null` into an `Optional` |
| **chain** | calls one after another, each on the previous result |
| **nested Optional** | `Optional<Optional<T>>`, a box in a box; `flatMap` avoids it |
| **pyramid of null checks** | nested `if (x != null)` blocks, which `flatMap` chains replace |
| **eager** vs **lazy default** | `orElse(x)` always works `x` out; `orElseGet(() -> x)` only when empty |
| **supplier** | a function with no arguments that produces a value: the "recipe" for a default |
| **unwrapping** | taking the value out with `get()`; risky, prefer to work inside the Optional |
| **return type only** | the rule: use `Optional` for what a method returns, not for fields or parameters |
| **serializable** | can be written out with Java's built-in object serialization; `Optional` is not |
| **allocation** | creating one more object in memory |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `javac Maybe.java && java Maybe` | builds and runs this lesson's file |

### Java classes and methods

| Name | What it does |
|---|---|
| `Optional.of(value)` | an Optional holding `value`; throws if it is `null` |
| `Optional.ofNullable(value)` | empty if `value` is `null` |
| `Optional.empty()` | an empty Optional |
| `opt.map(f)` | applies `f` to the value if present |
| `opt.flatMap(f)` | `map` for an `f` that itself returns an Optional |
| `opt.filter(p)` | keeps the value only if `p` is true for it |
| `opt.orElse(d)` | the value, or `d` |
| `opt.orElseGet(() -> ...)` | the value, or a default computed only when needed |
| `opt.orElseThrow()` | the value, or `NoSuchElementException` |
| `opt.orElseThrow(() -> new SomeException(...))` | the value, or your own exception |
| `opt.ifPresent(c)` | runs `c` with the value, if there is one |
| `opt.or(() -> other)` | this Optional if present, otherwise `other` |
| `opt.isPresent()`, `opt.get()` | the unsafe way: check, then unwrap |
| `map.get(key)` | `null` for a missing key |
| `s.isBlank()` | `true` for an empty or all-space string |
| `Optionals::expensive` | a method reference used as a supplier |

### Errors

| Error | Means |
|---|---|
| `NoSuchElementException` | `get()` or `orElseThrow()` on an empty Optional |
| `NullPointerException` | `Optional.of(null)`, or using a `null` that was returned instead of an Optional |

---

Tony Hoare, who introduced the null reference in 1965, later called it his
"billion-dollar mistake", for the crashes it has caused since.

`null` carries no information. A method returning `String` might return one,
might return `null`, and the signature does not say which — so every caller
either checks or eventually throws `NullPointerException`.

`Optional<T>` (Java 8) puts that fact in the type.

```java
Optional<String> found = lookup(key);
```

(A fragment: `lookup` stands for any method that might not find anything.)
An `Optional<String>` is a small container that holds either one `String` or
nothing; it is **present** or **empty**. Because the variable's type is
`Optional<String>` and not `String`, the caller cannot call `String` methods
on it directly. They cannot use the value without acknowledging it might not
be there, which is the entire benefit: the compiler, not a crash at 3 a.m.,
tells them to handle the missing case.

## Making one

```java
Optional.of(value)            // throws if value is null
Optional.ofNullable(value)    // empty if value is null
Optional.empty()
```

`of` is for values you know are present; using it on a nullable expression just
moves the `NullPointerException` earlier. `ofNullable` is the bridge from code
that uses `null`, such as `Map.get`, which returns `null` for a missing key:
`Optional.ofNullable(map.get(key))` turns that `null` into an empty Optional.

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

(Calls on some `Optional<String> opt`.) What each does:

- `map(f)` applies `f` to the value if there is one, and gives a new Optional
  of the result; on an empty Optional it does nothing and stays empty. That is
  what makes chains safe: `opt.map(String::length)` is an `Optional<Integer>`,
  present or empty to match.
- `filter(p)` keeps the value only if `p` is true for it, and is empty
  otherwise.
- `orElse(d)`, `orElseGet(s)` and `orElseThrow()` are the ways out: the value
  if present, otherwise a default, a computed default, or an exception.
- `ifPresent(c)` runs `c` with the value, only if there is one.
- `or(s)` (Java 9) is "this Optional if present, otherwise the Optional `s`
  supplies": a fallback that is itself optional.
- `flatMap(f)` is `map` for a function that itself returns an `Optional`.
  `map` would give an `Optional<Optional<...>>`, a box in a box; `flatMap`
  gives one box.
- `orElseThrow(() -> new SomeException(...))` throws an exception of your
  choosing when empty, with a useful message, instead of the generic
  `NoSuchElementException`.

It helps to think of an `Optional` as a stream that holds at most one element:
`map`, `filter` and `flatMap` mean the same as they do on streams.

The case `flatMap` exists for is a chain of lookups, each of which may find
nothing. Written with `null` checks it becomes a pyramid:

```java
// every step can be missing, so every step needs a check
User user = findUser(id);
if (user != null) {
    Address address = user.getAddress();
    if (address != null) {
        return address.getCity();
    }
}
return "unknown";
```

If `findUser` and `getAddress` return `Optional`s instead, the same logic is
one chain, and a missing value anywhere simply flows through as empty:

```java
return findUser(id)                     // Optional<User>
        .flatMap(User::getAddress)      // Optional<Address>: getAddress returns an Optional
        .map(Address::getCity)          // Optional<String>: getCity returns a plain String
        .orElse("unknown");
```

(Sketches: `findUser`, `User` and `Address` stand for your own code.) The
rule for choosing: `map` when the function returns a plain value, `flatMap`
when it returns an `Optional`.

`orElse` evaluates its argument **always**, even when the value is present;
`orElseGet` takes a supplier and only calls it when needed. If the default is
costly or has side effects, that difference is a bug rather than a style point.
It is not something special about `Optional`: Java always works out a method's
arguments before calling it, so `expensive()` runs before `orElse` even
starts. Passing a supplier, `() -> expensive()`, passes the *recipe* instead,
which `orElseGet` only follows when needed.

## Using one badly

```java
if (opt.isPresent()) { use(opt.get()); }
```

This is `null`-checking with extra ceremony and no safety: `get()` on an empty
Optional throws. Prefer `map`, `filter`, `ifPresent` and `orElse` — keep the
value inside the Optional and transform it there. The same logic, both ways:

```java
// unwrapping: two steps, and get() is a crash waiting for the check to go missing
int length;
if (opt.isPresent()) {
    length = opt.get().length();
} else {
    length = -1;
}

// keeping it inside: one expression, and nothing can throw
int length = opt.map(String::length).orElse(-1);
```

Two more rules from the API's designers:

- **Do not use `Optional` for fields or parameters.** It is a return type. It
  is not serializable (cannot be written out with Java's built-in object
  serialization) and it adds an allocation (an extra object) for no gain
  inside an object. A parameter of type `Optional` can itself be passed
  `null`, which defeats it entirely.
- **Never return `null` from a method that returns `Optional`.** That is the
  worst of both worlds, and it happens more than you would think.

## Run

```java
import java.util.NoSuchElementException;
import java.util.Optional;

public class Optionals {
    static String expensive() {
        System.out.println("computing default");
        return "default";
    }

    public static void main(String[] args) {
        Optional<String> some = Optional.of("value");
        System.out.println(some.orElse(expensive()));             // runs expensive()
        System.out.println(some.orElseGet(Optionals::expensive)); // does not

        Optional<String> none = Optional.ofNullable(null);
        System.out.println(none.map(String::length).orElse(-1));
        try {
            none.orElseThrow();
        } catch (NoSuchElementException e) {
            System.out.println("orElseThrow: NoSuchElementException");
        }
        try {
            Optional.of(null);
        } catch (NullPointerException e) {
            System.out.println("of(null): NullPointerException");
        }
    }
}
```

```output
computing default
value
value
-1
orElseThrow: NoSuchElementException
of(null): NullPointerException
```

`some.orElse(expensive())` printed "computing default" although `some` had a
value: the argument ran first, and its result was thrown away. `orElseGet`
was given `Optionals::expensive` as a supplier, and never called it. On the
empty Optional, `map` did nothing and `orElse(-1)` supplied the answer;
`orElseThrow()` threw; and `Optional.of(null)` failed immediately.

## Your turn

In `Maybe.java`:

- `public static Optional<String> find(Map<String, String> map, String key)` —
  the value for `key`, or an empty Optional (never `null`) when the key is
  missing
- `public static int nameLength(Map<String, String> map, String key)` — the
  length of the value for `key`, or -1 when it is missing. Build it from
  `find`, mapping inside the Optional.
- `public static Optional<String> firstNonBlank(Optional<String> a, Optional<String> b)`
  — `a` if it holds a non-blank string, otherwise `b` if it does, otherwise
  empty. A string of only spaces counts as blank, so `Optional.of("   ")` is
  skipped just like an empty Optional.
- `public static String requireValue(Optional<String> value)` — the value;
  throws `NoSuchElementException` when empty
- `public static String orDefault(Optional<String> value, String fallback)` —
  the value, or `fallback` when empty
