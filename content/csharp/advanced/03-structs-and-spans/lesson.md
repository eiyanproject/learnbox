---
title: Structs and spans
summary: Value types, where they are actually stored, and Span<T> - a window onto memory you already have, with no copy and no allocation.
order: 3
files: [Fast.cs]
run: dotnet build -c Release && dotnet bin/Release/net8.0/lesson.dll
hints:
  - "`public readonly struct Point` - readonly on the struct means every field is readonly and the compiler can skip defensive copies."
  - "`WithX` returns a new Point rather than mutating: a readonly struct cannot change, which is the point."
  - "A string converts implicitly to ReadOnlySpan<char>, so `SumDigits(\"a1b2\")` just works."
  - "Slice rather than Substring: `text.Slice(start, length)` is a window onto the same memory and allocates nothing."
---

## Value types

A `struct` is copied on assignment and on every method call. A `class` is a
reference — copying it copies the pointer.

```csharp
var a = new Point(1, 2);
var b = a;            // a full copy for a struct, a shared reference for a class
```

"Structs live on the stack" is the usual summary and it is not quite right. A
struct lives **where it is declared**: a local goes on the stack, a struct
field inside a class goes on the heap with that object, and a `Point[]` is one
heap block holding the points inline — no per-element object, no pointer chase.
That last one is the real performance argument.

Use a struct when the thing is small (roughly ≤ 16 bytes), immutable, and
genuinely a value — a coordinate, a money amount, a timestamp. `readonly
struct` is the form to prefer: without it, the compiler makes a defensive copy
every time it sees a method called on a readonly field, which quietly costs
more than the class would have.

A **mutable** struct is a documented mistake. `list[0].X = 5` modifies a copy
and silently does nothing.

## Span

```csharp
ReadOnlySpan<char> text = "hello world";
ReadOnlySpan<char> word = text.Slice(0, 5);
```

A `Span<T>` is a pointer and a length: a window onto memory that already
exists. Slicing allocates nothing and copies nothing, where `Substring` does
both.

It works over a string, an array, a `stackalloc` block or unmanaged memory —
one API for all of them:

```csharp
Span<int> scratch = stackalloc int[16];
```

## The restrictions

`Span<T>` is a `ref struct`: it may only ever live on the stack. So it cannot
be a field of a class, cannot be boxed, cannot be a generic type argument, and
**cannot cross an `await` or a `yield return`**.

Those are not arbitrary. If a span could outlive its stack frame it would point
at memory that no longer exists. The rules are what make it safe without a
garbage-collected object behind it.

For the async case there is `Memory<T>`, which can be a field and converts to a
span when you need one.

## Your turn

In `Fast.cs`:

- `readonly struct Point` — `X`, `Y`, `Length()`, `WithX(double)`
- `static int SumDigits(ReadOnlySpan<char> text)`
- `static bool TryParseInt(ReadOnlySpan<char> text, out int value)`
- `static int CountWords(ReadOnlySpan<char> text)` — slicing, no Split
- `static int SumOfSquares(int n)` — using `stackalloc`
