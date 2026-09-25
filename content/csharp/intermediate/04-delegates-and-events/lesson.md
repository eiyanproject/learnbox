---
title: Delegates and events
summary: Passing behaviour as a value - Func and Action, composition, closures, and the event that lets others listen without you knowing who.
order: 4
files: [Signals.cs]
run: dotnet build -c Release && dotnet bin/Release/net8.0/lesson.dll
hints:
  - "`Func<int, int>` takes an int and returns an int; `Action<string>` takes a string and returns nothing. The last type argument of Func is the return type."
  - "Compose with a lambda: `x => second(first(x))`."
  - "`Counter()` must return a lambda that captures a local - the local outlives the method because the closure holds it."
  - "Raise an event through `Threshold?.Invoke(this, value)`: null when nobody has subscribed."
---

A delegate is a typed reference to a method — behaviour you can store in a
variable, pass as an argument, and return.

## Func and Action

```csharp
Func<int, int> twice = x => x * 2;
Action<string> log = message => Console.WriteLine(message);
Predicate<int> isEven = n => n % 2 == 0;
```

`Func<..., TResult>` returns something; its **last** type argument is the
return type. `Action<...>` returns nothing. Between them they cover nearly
every case, which is why custom `delegate` declarations are rarer than they
used to be:

```csharp
public delegate int Transform(int value);   // same thing as Func<int, int>
```

They are still worth declaring when the name carries meaning, or when you need
`ref`/`out` parameters, which `Func` cannot express.

## Closures

```csharp
public static Func<int> Counter()
{
    int count = 0;
    return () => ++count;
}
```

The lambda captures `count` — the variable itself, not a copy. The local
outlives the method that declared it, because the compiler moves it onto the
heap in a generated class. Two calls to `Counter()` produce two independent
counters.

The classic trap was capturing a `for` loop variable, where every lambda shared
one variable and all saw the final value. `foreach` was fixed in C# 5 to
declare a fresh variable per iteration; a plain `for` loop still shares one.

## Multicast

Delegates combine:

```csharp
Action<string> both = first + second;
both -= first;
```

Every target runs in order. For a `Func`, only the **last** return value
survives — which is why multicast is almost always used with `Action`.

## Events

```csharp
public event EventHandler<decimal>? Threshold;
...
Threshold?.Invoke(this, value);
```

An `event` is a delegate field with the outside world restricted to `+=` and
`-=`. Subscribers cannot raise it, cannot clear the list, and cannot replace it
with `=`. Only the declaring type can invoke it.

The `?.` matters: an event with no subscribers is null, and invoking it
unguarded throws.

## Your turn

In `Signals.cs`:

- `static Func<int, int> Compose(Func<int, int> first, Func<int, int> second)`
- `static List<int> ApplyAll(IEnumerable<int> values, Func<int, int> f)`
- `static Func<int> Counter()`
- `class Gauge` with `event EventHandler<decimal>? Threshold`, a `Limit`, and
  `Record(decimal)`
