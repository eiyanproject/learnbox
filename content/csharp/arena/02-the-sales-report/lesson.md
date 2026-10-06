---
title: "Round 2: The sales report"
summary: Group, total, rank and average a list of sales. Three LINQ queries against the clock.
order: 2
files: [Report.cs]
run: dotnet build -c Release
challenge:
  minutes: 18
  xp: 200
  requires:
    xp: 250
---

The quarter closed an hour ago and the board meets in eighteen minutes.

## The task

`Report.cs` has the `Sale` record and the three method signatures of the
static class `Report`. Write the bodies.

```csharp
public record Sale(string Region, string Product, decimal Amount);
```

`List<(string Region, decimal Total)> TotalsByRegion(IEnumerable<Sale> sales)`
adds up the amounts per region. The list is ordered by total, largest first;
regions with the same total go in alphabetical order.

`string? BestProduct(IEnumerable<Sale> sales)` is the product with the
largest total amount. If several are level, the first alphabetically. `null`
when there are no sales.

`Dictionary<string, decimal> AverageByProduct(IEnumerable<Sale> sales)` maps
each product to the average amount of its sales, rounded to 2 decimals with
`Math.Round(value, 2)`.

```text
north  tea     10
south  tea      4
north  coffee  20
south  coffee   8.50

TotalsByRegion    ->  [("north", 30), ("south", 12.50)]
BestProduct       ->  "coffee"            (28.50 against 14)
AverageByProduct  ->  tea: 7, coffee: 14.25
```
