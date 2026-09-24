---
title: Lists, dictionaries and the collection interfaces
summary: Which collection to reach for, why a method should take IEnumerable, and the TryGetValue that avoids two lookups.
order: 2
files: [Store.cs]
run: dotnet build -c Release && dotnet bin/Release/net8.0/lesson.dll
hints:
  - "`CountWords` lowercases, splits on whitespace with `StringSplitOptions.RemoveEmptyEntries`, and counts into a Dictionary."
  - "Use `CollectionsMarshal` nothing fancy - `counts[word] = counts.GetValueOrDefault(word) + 1` is the readable one-liner."
  - "`FirstDuplicate` needs a HashSet: add each item and return the first one Add returns false for."
  - "Take `IEnumerable<T>` as a parameter and return `List<T>` or an array - accept the general, return the specific."
---

The collections are in `System.Collections.Generic` and the important ones are
few.

| Type | Use |
|---|---|
| `List<T>` | the default: indexed, growable |
| `Dictionary<K,V>` | key to value, O(1) average |
| `HashSet<T>` | membership and dedup |
| `Queue<T>` / `Stack<T>` | FIFO / LIFO |
| `T[]` | fixed size, when it truly is |

## Accept the general, return the specific

```csharp
public static int Total(IEnumerable<int> values)    // takes anything iterable
public static List<string> Names()                   // gives something concrete
```

`IEnumerable<T>` is the minimum a method needs to iterate, so taking it lets
callers pass a list, an array, a `HashSet` or a LINQ query with no conversion.
Returning it, by contrast, hides whether the result is already computed — and
if it is a lazy query, iterating twice does the work twice.

`IReadOnlyList<T>` is the middle ground when the caller needs indexing but must
not modify.

## Dictionary lookups

```csharp
if (counts.ContainsKey(k)) { total += counts[k]; }   // two lookups
if (counts.TryGetValue(k, out var n)) { total += n; } // one
counts.GetValueOrDefault(k, 0);                       // one, no out parameter
```

`TryGetValue` is the idiomatic form. `counts[missing]` throws
`KeyNotFoundException` for a read, but assigning to a missing key adds it —
read and write behave differently, which catches people out.

## The counting idiom

```csharp
counts[word] = counts.GetValueOrDefault(word) + 1;
```

## Iteration order

`Dictionary<K,V>` and `HashSet<T>` make **no guarantee** about order. It looks
stable in small tests and changes when the table resizes. If you need an order,
sort explicitly or use `SortedDictionary`.

## Your turn

In `Store.cs`, a `public static class Store` in `namespace Lesson`:

- `Dictionary<string,int> CountWords(string text)` — lowercase, whitespace
  separated
- `string? FirstDuplicate(IEnumerable<string> items)` — the first item seen
  twice, or null
- `List<T> Dedupe<T>(IEnumerable<T> items)` — first-seen order preserved
- `List<KeyValuePair<string,int>> TopWords(string text, int n)` — count
  descending, then word ascending
