---
title: Iterators and laziness
summary: yield return, what the compiler builds out of it, and why a query that never runs costs nothing.
order: 1
files: [Sequences.cs]
run: dotnet build -c Release && dotnet bin/Release/net8.0/lesson.dll
hints:
  - "A method containing `yield return` returns IEnumerable<T> and runs nothing until it is enumerated."
  - "`Naturals()` is an infinite loop - that is fine, because `Take(5)` stops asking."
  - "`yield break` ends the sequence early; falling off the end of the method does the same."
  - "`Counted` needs a field the tests can read, incremented each time an element is produced - that is how they observe the laziness."
---

```csharp
public static IEnumerable<int> Evens(IEnumerable<int> values)
{
    foreach (int n in values)
    {
        if (n % 2 == 0) yield return n;
    }
}
```

No list is built. `yield return` makes the compiler rewrite the method into a
state machine class implementing `IEnumerable<T>` and `IEnumerator<T>`, where
each `MoveNext()` runs your code up to the next `yield return` and then stops,
keeping the locals and the position in a field.

## Nothing runs until you ask

Calling the method does **not** execute the body. It builds the state machine
and returns. The body first runs at the first `MoveNext()` — which is what
`foreach`, `ToList()`, `Count()` and `First()` do.

Two consequences that surprise people:

- An argument check inside an iterator method does not fire at the call. If you
  want eager validation, put it in a normal method that returns the iterator
  from a private one.
- Enumerating twice runs the body twice. `ToList()` if the source is expensive
  or changing.

## Infinity is allowed

```csharp
public static IEnumerable<int> Naturals()
{
    int n = 1;
    while (true) yield return n++;
}
```

Perfectly well-behaved, because nothing computes an element nobody asked for.
`Naturals().Where(IsPrime).Take(5)` does exactly the work needed for five
primes and then stops.

This is the whole reason LINQ is lazy: operators compose into a pipeline, and
the pipeline pulls one element at a time from the back.

## The cost

Laziness is not free. Each element goes through a `MoveNext()` call per stage
of the pipeline, and a five-stage query pays that five times per element. For
a hot loop over a `List<int>`, a plain `for` is measurably faster.

Reach for laziness when the sequence is large, infinite, expensive, or might
not be fully consumed. Not because it reads better.

## Your turn

In `Sequences.cs`:

- `static IEnumerable<int> Evens(IEnumerable<int> values)`
- `static IEnumerable<int> Naturals()` — infinite
- `static IEnumerable<T> TakeUntil<T>(IEnumerable<T> values, Func<T, bool> stop)` —
  stops *before* the first match, using `yield break`
- `class Counted : IEnumerable<int>` — wraps a list, exposes `Produced`
