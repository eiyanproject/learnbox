---
title: Lambdas and functional interfaces
summary: What a lambda actually is, the four interfaces the API is built from, and the four shapes of method reference.
order: 3
files: [Funcs.java]
run: javac Funcs.java && java Funcs
hints:
  - "A functional interface has exactly ONE abstract method. `@FunctionalInterface` makes the compiler enforce it."
  - "`applyTwice(UnaryOperator<Integer> f, int x)` is `f.apply(f.apply(x))`."
  - "`describeAll(List<String>, Function<String,String>)` maps each item through the function into a new list."
  - "`counter()` returns a Supplier<Integer> that increments a captured value - use an int[] or AtomicInteger, because a captured local must be effectively final."
---

A lambda is an implementation of an interface with one abstract method, written
as an expression:

```java
Runnable r = () -> System.out.println("hi");
Comparator<String> byLength = (a, b) -> a.length() - b.length();
```

It is **not** a closure over mutable state. A lambda may capture a local
variable only if it is *effectively final* — assigned once and never
reassigned. Capture a field or an array element if you need to mutate
something, which is exactly what the counter exercise below forces you to
discover.

## The four shapes

Almost all of `java.util.function` is a variation on four ideas:

| Interface | Method | Takes | Returns |
|---|---|---|---|
| `Supplier<T>` | `get()` | nothing | T |
| `Consumer<T>` | `accept(t)` | T | nothing |
| `Function<T,R>` | `apply(t)` | T | R |
| `Predicate<T>` | `test(t)` | T | boolean |

Plus the arity and primitive variants: `BiFunction<T,U,R>`,
`UnaryOperator<T>` (a `Function<T,T>`), `BinaryOperator<T>`, and `IntPredicate`
and friends, which exist to avoid boxing.

`Function` composes: `f.andThen(g)` runs f first, `f.compose(g)` runs g first.
`Predicate` has `and`, `or` and `negate`.

## Method references

Four forms, and the exam expects you to recognise all four:

```java
String::toUpperCase      // an instance method of the parameter
System.out::println      // an instance method of a specific object
Integer::parseInt        // a static method
ArrayList::new           // a constructor
```

`String::toUpperCase` is the interesting one: the receiver becomes the lambda's
argument, so it is a `Function<String,String>` even though `toUpperCase` takes
none.

## Run

```java
import java.util.ArrayList;
import java.util.List;
import java.util.function.*;

public class Lambdas {
    public static void main(String[] args) {
        Function<Integer, Integer> plus1 = x -> x + 1, times2 = x -> x * 2;
        System.out.println(plus1.andThen(times2).apply(5) + " " + plus1.compose(times2).apply(5));

        Function<String, String> upper = String::toUpperCase;
        Function<String, Integer> parse = Integer::parseInt;
        Supplier<List<String>> make = ArrayList::new;
        List<String> list = make.get();
        list.add(upper.apply("hi"));
        list.forEach(System.out::println);
        System.out.println(parse.apply("41") + 1);

        Predicate<String> empty = String::isEmpty;
        System.out.println(empty.negate().test("") + " " + empty.or(s -> s.startsWith("a")).test("abc"));

        int[] counter = {0};              // a local int could not be changed here
        Runnable bump = () -> counter[0]++;
        bump.run();
        bump.run();
        System.out.println(counter[0]);
    }
}
```

```output
12 11
HI
42
false true
2
```

## Your turn

In `Funcs.java`:

- `@FunctionalInterface interface Transformer { String apply(String input); }`
- `public static String transform(String s, Transformer t)`
- `public static int applyTwice(UnaryOperator<Integer> f, int x)`
- `public static List<String> describeAll(List<String> items, Function<String, String> f)`
- `public static List<String> keep(List<String> items, Predicate<String> test)`
- `public static Supplier<Integer> counter()` — each `get()` returns 1, 2, 3...
