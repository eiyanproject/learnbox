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

Generics move type errors from runtime to compile time. Before them (Java 5),
every collection held `Object` and every read needed a cast that might fail.
This is what that looked like, and still compiles today as a **raw type**, a
generic class used without its type parameter:

```java
import java.util.*;

public class Raw {
    @SuppressWarnings({"rawtypes", "unchecked"})
    public static void main(String[] args) {
        List names = new ArrayList();      // no type parameter: holds Object
        names.add("Ada");
        names.add(42);                     // nothing stops this
        for (Object o : names) {
            try {
                String s = (String) o;     // the cast that every read needed
                System.out.println(s.toUpperCase());
            } catch (ClassCastException e) {
                System.out.println("ClassCastException at run time");
            }
        }
    }
}
```

```output
ADA
ClassCastException at run time
```

The mistake, putting a number into a list of names, happened on one line,
but it was only discovered later, on a different line, while running. With
`List<String> names`, `names.add(42)` is a compile error on the line that is
actually wrong, and no cast is needed when reading. That is the whole point
of generics. (`@SuppressWarnings` hides the compiler's warnings about raw
types, which exist precisely because this is unsafe.)

A **generic class** has a **type parameter**, written in angle brackets after
its name, which stands for a type the user of the class chooses:

```java
class Box<T> {
    private T value;
    T get() { return value; }
    void set(T value) { this.value = value; }
}
```

`T` is a placeholder filled in at each use: `Box<String>`, `Box<Integer>`. In
a `Box<String>`, `get()` returns a `String` and `set` only accepts one. A good
way to read a generic class is to substitute the argument for `T` in your
head. For `Box<String>`, the compiler checks your code as if you had written:

```java
class Box {                    // Box<String>, as the compiler checks it
    private String value;
    String get() { return value; }
    void set(String value) { this.value = value; }
}
```

This is only the compile-time view. At run time there is one `Box` class,
which holds an `Object`, as the next section explains. Type
parameters are written as single capital letters by convention: `T` for
type, `E` for element, `K` and `V` for key and value. Type arguments must be
reference types, so it is `Box<Integer>`, never `Box<int>`; boxing fills the
gap.

`new Box<>()`, with empty angle brackets (the **diamond**), lets the compiler
fill in the type argument from the variable's declared type.

## Erasure, and what it costs

Generics exist only at compile time. The compiler checks your types, then
**erases** them — `Box<String>` and `Box<Integer>` are the same class at
runtime. Three consequences the exam asks about:

- `new T()` is impossible; there is no `T` at runtime.
- `new T[10]` is impossible for the same reason.
- `list instanceof List<String>` does not compile — only `List<?>` does.

Erasure is why generics interoperate with pre-generic code, and why they cannot
do everything a **reified** system could (one that keeps the type arguments at
run time, as C# does). Under erasure, `T` inside `Box` is compiled as
`Object`, and the compiler inserts the casts at each call site for you, the
same casts the raw-type program wrote by hand, except that the compiler has
already proved they cannot fail.

## Wildcards, and PECS

A `List<Integer>` is **not** a `List<Number>`, even though an `Integer` is a
`Number`. If it were, you could add a `Double` to it through the wider
reference and break the original:

```java
List<Integer> ints = new ArrayList<>();
List<Number> nums = ints;      // if this compiled...
nums.add(2.5);                 // ...a Double would now be in ints
```

So the second line is refused:
`incompatible types: List<Integer> cannot be converted to List<Number>`. This
is called **invariance**: a generic type is unrelated to the same generic
type with a different argument, whatever the relationship between the
arguments.

That is safe, but too strict for a method that only wants to *read* numbers
from any list of numbers. **Wildcards** (`?`, meaning "some unknown type")
restore the flexibility safely:

```java
double sum(List<? extends Number> values)   // read Numbers out
void fill(List<? super Integer> target)     // write Integers in
```

(Method headers.) `List<? extends Number>` means "a list of some type that is
`Number` or a subclass of it": `List<Integer>`, `List<Double>` and
`List<Number>` all qualify. `List<? super Integer>` means "a list of some
type that is `Integer` or a parent of it": `List<Integer>`, `List<Number>`
and `List<Object>`.

**PECS — Producer Extends, Consumer Super.** If the parameter *produces* values
for you to read, use `extends`. If it *consumes* values you put in, use
`super`.

The restriction follows from the same argument: with `? extends Number` the
list might be `List<Double>`, so adding an `Integer` must be refused — you can
read, not write. With `? super Integer` it might be `List<Object>`, so anything
you read is only guaranteed to be an `Object`.

The compiler's message for the refused write is cryptic, so it helps to
recognise it. `values.add(1)` on a `List<? extends Number>` gives:

```text
error: incompatible types: int cannot be converted to CAP#1
```

`CAP#1` is the compiler's name for "the unknown type the `?` stands for"
(the wildcard **captured** as a type). It cannot prove `1` belongs in a list
of that unknown type, so it refuses.

`Collections.copy(List<? super T> dest, List<? extends T> src)` in the
standard library is PECS in one line: it reads from `src` and writes into
`dest`.

## Bounded type parameters

```java
<T extends Comparable<T>> T max(List<T> list)
```

This is a **generic method**: its type parameter, `<T ...>`, is written before
the return type, and is worked out afresh from the arguments at each call.
`max(List.of(3, 9))` makes `T` an `Integer`; `max(List.of("a", "b"))` makes it
a `String`.

The **bound**, `extends Comparable<T>`, says what you may *do* with `T` — here,
call `compareTo`, the method of `Comparable` that orders two objects (negative
if this one comes first, zero if equal, positive if it comes after). Without
it `T` is only an `Object`, and `t.compareTo(...)` does not compile. In a
bound, `extends` is used for interfaces as well as classes. A parameter may
have several bounds with `&`, such as `<T extends Number & Comparable<T>>`.

## Run

```java
import java.util.ArrayList;
import java.util.List;

public class Generics {
    static class Box<T> { T value; }

    static double sum(List<? extends Number> values) {
        double total = 0;
        for (Number n : values) total += n.doubleValue();
        return total;
    }

    static void fill(List<? super Integer> target) {
        for (int i = 1; i <= 3; i++) target.add(i);
    }

    static <T extends Comparable<T>> T max(List<T> list) {
        T best = list.get(0);
        for (T t : list) if (t.compareTo(best) > 0) best = t;
        return best;
    }

    public static void main(String[] args) {
        // erased: one class at run time
        System.out.println(new Box<String>().getClass() == new Box<Integer>().getClass());
        System.out.println(sum(List.of(1, 2.5, 3L)));
        List<Object> sink = new ArrayList<>();
        fill(sink);                                 // a List<Object> consumes Integers
        System.out.println(sink);
        System.out.println(max(List.of("pear", "apple", "plum")));
    }
}
```

```output
true
6.5
[1, 2, 3]
plum
```

The two `Box` objects have different type arguments but one class at run
time, which is erasure. `List.of(1, 2.5, 3L)` holds an `Integer`, a `Double`
and a `Long`, all `Number`s, so `sum` can read each as a `Number` and call
`doubleValue()`. A `List<Object>` accepts `Integer`s, so `fill` can write
into it through `? super Integer`. And strings compare alphabetically, so
`plum` is the largest of the three.

## Your turn

In `Boxes.java`:

- `public static class Box<T>`, nested inside `Boxes` (the tests write
  `Boxes.Box<String>`), with a constructor taking the starting value, `get()`
  and `set(T)`
- `public static double sumAll(List<? extends Number> values)` — the total of
  the values as a `double`, `0.0` for an empty list. It must accept a
  `List<Integer>` and a `List<Double>` alike.
- `public static void addNumbers(List<? super Integer> target, int count)` —
  adds the whole numbers 1 to `count`, in order, to the end of `target`. It
  must accept a `List<Integer>` and wider lists such as a `List<Number>`.
- `public static <T> T firstOrDefault(List<T> list, T fallback)` — the first
  element, or `fallback` for an empty list
- `public static <T extends Comparable<T>> T largest(List<T> list)` — the
  largest element by `compareTo`, for any comparable type (`9` from
  `{3, 9, 4}`, `"pear"` from `{"apple", "pear", "fig"}`). An empty list throws
  `IllegalArgumentException`.
