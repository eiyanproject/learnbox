---
title: Interfaces and generics
summary: Describing a capability rather than a class, and writing code once for every type that has it.
order: 1
files: [Store.cs]
run: dotnet build -c Release && dotnet bin/Release/net8.0/lesson.dll
hints:
  - "`Repository<T>` needs `where T : class, IIdentified` - without the constraint the compiler does not know T has an Id."
  - "`TryGet` follows the framework's Try pattern: return bool, assign the out parameter on both paths (null when it fails)."
  - "`Largest<T>` needs `where T : IComparable<T>` so you can call `a.CompareTo(b)`."
  - "An interface member is public by definition - do not write `public` on it, and do write it on the implementing class."
---

An interface names a capability. A class that has it declares so, and code can
then require the capability rather than the class.

```csharp
public interface IIdentified
{
    int Id { get; }
}
```

No access modifiers: interface members are public by definition. No bodies,
usually — C# 8 allows default implementations, but they are for versioning an
existing interface without breaking implementers, not a first choice.

## Why not a base class

A class has one base and many interfaces. More importantly, a base class says
*what something is* and an interface says *what it can do*. `IDisposable` is
not a kind of thing; it is a thing you can dispose.

The framework is built this way: `IEnumerable<T>`, `IComparable<T>`,
`IDisposable`. Implement them and the language itself cooperates — `foreach`
works on anything enumerable, `using` on anything disposable.

## Generics

```csharp
public class Repository<T> where T : class, IIdentified
```

One implementation, every element type, with no casting and no boxing. C#
generics are **reified**: `List<int>` really is a list of `int` at run time,
with the storage and the type check to match. This is unlike Java, where
erasure means `List<int>` cannot exist at all and `List<Integer>` boxes every
element.

`typeof(T)` therefore works, and so does `new T[16]`.

## Constraints

Without one, `T` could be anything, so you can do almost nothing with it. The
constraint is what buys you the members:

| | |
|---|---|
| `where T : class` | a reference type |
| `where T : struct` | a value type |
| `where T : IComparable<T>` | has `CompareTo` |
| `where T : new()` | has a parameterless constructor |

## The Try pattern

```csharp
public bool TryGet(int id, out Item? item)
```

Returns whether it worked and hands back the value through `out`. The
framework uses this wherever failure is ordinary — `int.TryParse`,
`Dictionary.TryGetValue` — because an exception for a missed lookup is both
slow and wrong. Assign the `out` parameter on **every** path, including the
failure one; the compiler requires it.

## Your turn

In `Store.cs`:

- `interface IIdentified` with `int Id { get; }`
- `record Item(int Id, string Name, decimal Price) : IIdentified`
- `class Repository<T> where T : class, IIdentified` — `Add`, `TryGet`,
  `Remove`, `Count`, `All()`
- `static T? Largest<T>(IEnumerable<T> items) where T : class, IComparable<T>`
