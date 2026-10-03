---
title: LINQ
summary: Query operators over any sequence, deferred execution and what it means for when the work happens.
order: 3
files: [Query.cs]
run: dotnet build -c Release && dotnet bin/Release/net8.0/lesson.dll
hints:
  - "`Where` filters, `Select` transforms, `OrderBy` sorts. Each returns a new sequence; none of them modifies the source."
  - "`ToList()` is what actually runs the query - without it you have a description of work, not a result."
  - "`GroupBy(x => key)` gives IGrouping<TKey, TElement>, which is itself enumerable: `g.Key` and `g.Count()`."
  - "Use `FirstOrDefault` rather than `First` when the sequence might be empty - First throws, FirstOrDefault returns null or the default."
---

LINQ is a set of extension methods on `IEnumerable<T>` that read as a query:

```csharp
var names = people
    .Where(p => p.Age >= 18)
    .OrderBy(p => p.Name)
    .Select(p => p.Name)
    .ToList();
```

## Deferred execution

This is the part that surprises people. `Where` and `Select` do **nothing**
when called — they build a description. The work happens when something
enumerates it:

```csharp
var query = people.Where(p => p.Age > 18);   // no work yet
var list = query.ToList();                    // now it runs
```

Two consequences:

- **The query sees the source as it is when enumerated.** Add to the list after
  building the query and the result includes the new item.
- **Enumerating twice does the work twice.** For an in-memory list that is
  waste; for a database query it is a second round trip. `ToList()` once and
  reuse.

## The operators worth knowing

| | |
|---|---|
| `Where` / `Select` | filter / transform |
| `SelectMany` | flatten nested sequences |
| `OrderBy` / `ThenBy` / `OrderByDescending` | sorting |
| `GroupBy` | into `IGrouping<K,T>` |
| `Any` / `All` / `Count` | predicates and counting |
| `First` / `FirstOrDefault` / `Single` | one element |
| `Sum` / `Average` / `Min` / `Max` | aggregation |
| `Take` / `Skip` / `Distinct` | slicing |
| `ToList` / `ToArray` / `ToDictionary` | materialise |

`First` throws when nothing matches; `FirstOrDefault` returns `null` or the
type's default. `Single` additionally throws when there is more than one — use
it when "exactly one" is the invariant you want checked.

Deferred execution and these three, demonstrated:

```csharp
var ages = new List<int> { 15, 30, 42 };
var adults = ages.Where(age => age > 18);      // no work yet
ages.Add(70);                                  // added after the query was built
Console.WriteLine(string.Join(",", adults));   // ...and it is included

int calls = 0;
var traced = ages.Select(x => { calls++; return x; });
traced.ToList();
traced.ToList();
Console.WriteLine(calls);                      // 4 items, enumerated twice

var small = new[] { 1, 2 };
Console.WriteLine(small.FirstOrDefault(x => x > 5));
try { small.First(x => x > 5); }
catch (InvalidOperationException) { Console.WriteLine("First threw"); }
try { new[] { 1, 1 }.Single(x => x == 1); }
catch (InvalidOperationException) { Console.WriteLine("Single threw"); }
```

```output
30,42,70
8
0
First threw
Single threw
```

## Query syntax

```csharp
var names = from p in people where p.Age >= 18 orderby p.Name select p.Name;
```

The same thing, compiled to the same calls. Method syntax is more common and
covers more operators; query syntax reads better for joins and multiple `from`
clauses.

## Your turn

In `Query.cs`, a `public static class Query` in `namespace Lesson`, given
`public record Person(string Name, int Age, string City)`:

- `List<string> AdultNames(IEnumerable<Person> people)` — 18 and over, sorted
- `Dictionary<string,int> CountByCity(IEnumerable<Person> people)`
- `double AverageAge(IEnumerable<Person> people)` — 0 for an empty sequence
- `Person? Oldest(IEnumerable<Person> people)` — null when empty
- `List<string> CitiesWithAtLeast(IEnumerable<Person> people, int n)` — sorted
