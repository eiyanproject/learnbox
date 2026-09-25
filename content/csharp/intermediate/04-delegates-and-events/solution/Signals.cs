namespace Lesson;

public static class Signals
{
    // first, then second - the order reads left to right at the call site.
    public static Func<int, int> Compose(Func<int, int> first, Func<int, int> second) =>
        x => second(first(x));

    public static List<int> ApplyAll(IEnumerable<int> values, Func<int, int> f) =>
        values.Select(f).ToList();

    public static Func<int> Counter()
    {
        // The lambda captures the variable itself, not its value, so count
        // outlives this method on the heap. Each call gets its own.
        int count = 0;
        return () => ++count;
    }
}

public class Gauge
{
    public Gauge(decimal limit) => Limit = limit;

    public decimal Limit { get; }

    public decimal Last { get; private set; }

    /// <summary>Raised whenever a recorded value exceeds Limit.</summary>
    public event EventHandler<decimal>? Threshold;

    public void Record(decimal value)
    {
        Last = value;
        if (value > Limit)
        {
            // Null when nobody has subscribed, so the ?. is not optional.
            Threshold?.Invoke(this, value);
        }
    }
}
