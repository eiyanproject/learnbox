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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **interface** | names a capability; a class declares that it has it |
| **access modifier** | `public`, `private`...; interface members are public by definition |
| **default implementation** | an interface method with a body (C# 8), for versioning |
| **base class** | the one class a class inherits from |
| **`IDisposable`** | can be disposed; `using` works on it |
| **`IComparable<T>`** | has `CompareTo` for ordering |
| **generics** | one implementation for every element type |
| **type parameter** | `T` in `Repository<T>` |
| **boxing** | wrapping a value type in an object; generics avoid it |
| **reified** | `List<int>` really is a list of `int` at run time |
| **type erasure** | Java's approach, where generic types vanish at run time |
| **constraint** | `where T : ...`: what `T` must be, which buys you its members |
| **parameterless constructor** | a constructor with no arguments, required by `new()` |
| **Try pattern** | return whether it worked, and the value through `out` |
| **`out` parameter** | a parameter the method must assign on every path |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `dotnet build -c Release` | compiles the project in Release mode |
| `dotnet bin/Release/net8.0/lesson.dll` | runs the compiled program |

### C# names

| Name | What it does |
|---|---|
| `public interface IIdentified { int Id { get; } }` | an interface |
| `record Item(...) : IIdentified` | a record implementing it |
| `class Repository<T> where T : class, IIdentified` | a constrained generic class |
| `where T : class`, `struct`, `IComparable<T>`, `new()` | the common constraints |
| `typeof(T).Name` | the type's name at run time |
| `new T[n]` | an array of `T` |
| `int.TryParse("42", out var a)` | the framework's Try pattern |
| `public bool TryGet(int id, out Item? item)` | your own Try method |
| `T?` | may be null |

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

`typeof(T)` therefore works, and so does `new T[16]`:

```csharp
Console.WriteLine(NameOf<int>());
Console.WriteLine(NameOf<string>());
Console.WriteLine(Make<double>(3).GetType());

Console.WriteLine(int.TryParse("42", out var a) + " " + a);
Console.WriteLine(int.TryParse("x", out var b) + " " + b);

static string NameOf<T>() => typeof(T).Name;
static T[] Make<T>(int n) => new T[n];
```

```output
Int32
String
System.Double[]
True 42
False 0
```

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
