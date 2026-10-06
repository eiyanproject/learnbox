namespace Lesson;

public class Garage
{
    private readonly int _capacity;
    private readonly Dictionary<string, (int Slot, DateTime Arrived)> _cars = new();

    public Garage(int capacity)
    {
        if (capacity < 1)
        {
            throw new ArgumentOutOfRangeException(nameof(capacity));
        }
        _capacity = capacity;
    }

    private static string Tidy(string plate)
    {
        if (string.IsNullOrWhiteSpace(plate))
        {
            throw new ArgumentException("a plate is required", nameof(plate));
        }
        return plate.Trim().ToUpperInvariant();
    }

    public int Park(string plate, DateTime at)
    {
        var key = Tidy(plate);
        if (_cars.ContainsKey(key))
        {
            throw new InvalidOperationException($"{key} is already inside");
        }
        if (_cars.Count >= _capacity)
        {
            throw new InvalidOperationException("the garage is full");
        }
        var taken = _cars.Values.Select(c => c.Slot).ToHashSet();
        var slot = Enumerable.Range(1, _capacity).First(n => !taken.Contains(n));
        _cars[key] = (slot, at);
        return slot;
    }

    public decimal Leave(string plate, DateTime at)
    {
        var key = Tidy(plate);
        if (!_cars.TryGetValue(key, out var car))
        {
            throw new KeyNotFoundException($"{key} is not inside");
        }
        if (at < car.Arrived)
        {
            throw new ArgumentException("leaving before arriving", nameof(at));
        }
        _cars.Remove(key);
        var fee = Fee(at - car.Arrived);
        Takings += fee;
        return fee;
    }

    private static decimal Fee(TimeSpan stay)
    {
        if (stay <= TimeSpan.FromMinutes(30))
        {
            return 0m;
        }
        var hours = (decimal)Math.Ceiling(stay.TotalMinutes / 60);
        return Math.Min(20m, 2m * hours);
    }

    public bool IsParked(string plate) => _cars.ContainsKey(Tidy(plate));

    public int Free => _capacity - _cars.Count;

    public IReadOnlyList<string> Plates => _cars.Keys.OrderBy(p => p, StringComparer.Ordinal).ToList();

    public decimal Takings { get; private set; }
}
