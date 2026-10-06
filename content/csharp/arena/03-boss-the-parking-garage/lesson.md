---
title: "Boss: The parking garage"
summary: Slots, number plates, a fee table and every way the barrier can refuse a car.
order: 3
files: [Garage.cs]
run: dotnet build -c Release
challenge:
  boss: true
  minutes: 30
  xp: 500
  requires:
    xp: 500
---

The garage's old controller died in the night. Cars are queueing at the
barrier and the new one has to be running in half an hour.

## The task

In `Garage.cs`, finish the `Garage` class. The members are declared; the
bodies and the fields are yours.

### Setting up

`new Garage(capacity)` makes a garage with slots numbered `1` to `capacity`.
A capacity below 1 throws `ArgumentOutOfRangeException`.

### Plates

A plate is tidied before anything else: surrounding spaces are removed and
it is upper-cased, so `" ab-123 "` and `"AB-123"` are the same car. A plate
that is empty or only spaces throws `ArgumentException` wherever a plate is
given.

### Arriving

`int Park(string plate, DateTime at)` parks a car and returns its slot: the
**lowest-numbered** free one.

- a car that is already inside throws `InvalidOperationException`
- a full garage throws `InvalidOperationException`

### Leaving

`decimal Leave(string plate, DateTime at)` lets a car out, frees its slot
and returns the fee.

- a car that is not inside throws `KeyNotFoundException`
- a leaving time before the arrival time throws `ArgumentException`, and the
  car stays parked

The fee depends on how long the car stayed:

| Stay | Fee |
|---|---|
| up to and including 30 minutes | `0` |
| longer | `2.00` for every hour started |
| at most | `20.00` |

So 31 minutes and 60 minutes both cost `2.00`, 61 minutes costs `4.00`, and
anything from just over 9 hours upwards costs `20.00`.

### Looking

- `bool IsParked(string plate)`
- `int Free`: how many slots are empty
- `IReadOnlyList<string> Plates`: the tidied plates of the cars inside, in
  alphabetical order
- `decimal Takings`: the total of every fee charged so far

```csharp
var garage = new Garage(2);
var nine = new DateTime(2026, 3, 4, 9, 0, 0);
garage.Park("ab-123", nine);                  // 1
garage.Park("XY-9", nine);                    // 2
garage.Leave("AB-123", nine.AddMinutes(61));  // 4.00
garage.Park("new-1", nine.AddHours(2));       // 1 again: the lowest free slot
garage.Takings;                               // 4.00
```
