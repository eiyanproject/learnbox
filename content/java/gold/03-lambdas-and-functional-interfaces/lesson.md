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

Many methods need to be handed a piece of behaviour rather than a value:
how to sort, what to do for each element, which items to keep. Before Java 8
the only way to pass behaviour was an object implementing an interface, and
writing one took an **anonymous class**, a class with no name declared on the
spot. Sorting strings by length looked like this:

```java
Comparator<String> byLength = new Comparator<String>() {
    @Override
    public int compare(String a, String b) {
        return a.length() - b.length();
    }
};
```

Five lines, of which one says anything: `a.length() - b.length()`. The rest
is ceremony. A **lambda** keeps only the essence:

```java
Runnable r = () -> System.out.println("hi");
Comparator<String> byLength = (a, b) -> a.length() - b.length();
```

(Fragments.) A lambda is an implementation of an interface with one abstract
method, written as an expression. The parameters go before the arrow `->`,
in brackets (the brackets may be left out for exactly one parameter, as in
`x -> x + 1`), and the body after it. A single expression is returned
automatically; a body in braces needs its own `return`, as in
`(a, b) -> { int d = a.length() - b.length(); return d; }`. The parameter
types are usually left out, because the compiler knows them from the
interface: a `Comparator<String>` compares two `String`s, so `a` and `b` are
`String`s.

An interface with exactly one abstract method is a **functional interface**,
and only those can be implemented by a lambda, since a lambda supplies one
method body. `@FunctionalInterface` on an interface asks the compiler to
check that: giving such an interface a second abstract method fails with
`Unexpected @FunctionalInterface annotation`. `Comparator` and `Runnable` are
functional interfaces; the next section lists the general-purpose ones.

A lambda is **not** a closure over mutable state. A lambda may capture a local
variable (use one from the surrounding method) only if it is *effectively
final* — assigned once and never reassigned, whether or not it is declared
`final`. Breaking that is a compile-time error:

```text
error: local variables referenced from a lambda expression must be final or effectively final
    Runnable r = () -> n++;
                       ^
```

The reason is that the lambda may run later, after the method has returned
and its local variables are gone, so it is given a copy of the value; letting
either side change it would make the copy silently go stale. Capture a field
or an array element if you need to mutate something: the array reference
itself never changes, only what is inside it. That is exactly what the counter
exercise below forces you to discover.

## The four shapes

Almost all of `java.util.function` is a variation on four ideas:

| Interface | Method | Takes | Returns |
|---|---|---|---|
| `Supplier<T>` | `get()` | nothing | T |
| `Consumer<T>` | `accept(t)` | T | nothing |
| `Function<T,R>` | `apply(t)` | T | R |
| `Predicate<T>` | `test(t)` | T | boolean |

Read the names as what they do: a **supplier** produces values from nothing
(a factory, a counter), a **consumer** uses a value up and returns nothing
(printing, saving), a **function** turns one value into another, and a
**predicate** answers yes or no about a value (a filter).

Plus the arity and primitive variants. **Arity** is how many arguments a
function takes: `BiFunction<T,U,R>` takes two, a `T` and a `U`.
`UnaryOperator<T>` is a `Function<T,T>`, whose result has the same type as its
argument, and `BinaryOperator<T>` takes two `T`s and returns a `T` (as `+`
does). `IntPredicate` and friends take or return primitives directly, and
exist to avoid boxing every `int` into an `Integer`.

These interfaces also have **default methods** for combining them.
`Function` composes: `f.andThen(g)` runs f first, then g on the result;
`f.compose(g)` runs g first. `Predicate` has `and`, `or` and `negate`, so
`isEmpty.negate()` is "is not empty".

## Method references

When a lambda does nothing but call one existing method, a **method
reference**, `Class::method`, says the same more briefly. Four forms, and the
exam expects you to recognise all four, each shown with the lambda it stands
for:

```java
String::toUpperCase      // an instance method of the parameter     s -> s.toUpperCase()
System.out::println      // an instance method of a specific object x -> System.out.println(x)
Integer::parseInt        // a static method                        s -> Integer.parseInt(s)
ArrayList::new           // a constructor                          () -> new ArrayList<>()
```

`String::toUpperCase` is the interesting one: the receiver (the object the
method is called on) becomes the lambda's argument, so it is a
`Function<String,String>` even though `toUpperCase` takes none. Which form a
reference is depends on what is on the left of the `::`: a class name with an
instance method means "the parameter's own method", while an object, like
`System.out`, means "that object's method".

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

The working: `plus1.andThen(times2)` adds one, then doubles: `(5 + 1) * 2` is
12. `plus1.compose(times2)` doubles first: `5 * 2 + 1` is 11. `ArrayList::new`
as a `Supplier` made a new list, `String::toUpperCase` as a `Function` turned
`"hi"` into `"HI"`, and `forEach(System.out::println)` printed each element.
`"".isEmpty()` is true, so its negation is false; `"abc"` is not empty but does
start with `a`, so the `or` is true. And the lambda changed the array's
element, which is allowed, rather than reassigning a local variable, which is
not.

## Your turn

In `Funcs.java`:

- `@FunctionalInterface interface Transformer { String apply(String input); }`,
  declared inside `Funcs` (the tests refer to `Funcs.Transformer`)
- `public static String transform(String s, Transformer t)` — the result of
  applying `t` to `s`. It must work with a lambda and with a method reference
  such as `String::toUpperCase`.
- `public static int applyTwice(UnaryOperator<Integer> f, int x)` — `f`
  applied to `x`, then applied again to that result: doubling 2 twice gives 8
- `public static List<String> describeAll(List<String> items, Function<String, String> f)`
  — a new list holding `f` applied to each item, in order; the input list must
  not change
- `public static List<String> keep(List<String> items, Predicate<String> test)`
  — a new list of the items for which `test` is true, in order
- `public static Supplier<Integer> counter()` — each `get()` returns 1, 2, 3...
  Each call to `counter()` makes a fresh, independent counter that starts
  again at 1.
