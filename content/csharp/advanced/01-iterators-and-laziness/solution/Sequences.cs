using System.Collections;

namespace Lesson;

public static class Sequences
{
    // The body does not run here - calling this only builds the state machine
    // the compiler generated from the yield returns.
    public static IEnumerable<int> Evens(IEnumerable<int> values)
    {
        foreach (int n in values)
        {
            if (n % 2 == 0)
            {
                yield return n;
            }
        }
    }

    // Infinite, and harmless: nothing computes an element nobody asked for.
    public static IEnumerable<int> Naturals()
    {
        int n = 1;
        while (true)
        {
            yield return n++;
        }
    }

    public static IEnumerable<T> TakeUntil<T>(IEnumerable<T> values, Func<T, bool> stop)
    {
        foreach (T value in values)
        {
            if (stop(value))
            {
                yield break;
            }
            yield return value;
        }
    }
}

/// <summary>A sequence that records how many elements it has actually produced.</summary>
public class Counted : IEnumerable<int>
{
    private readonly IReadOnlyList<int> _values;

    public Counted(IReadOnlyList<int> values) => _values = values;

    public int Produced { get; private set; }

    public IEnumerator<int> GetEnumerator()
    {
        foreach (int value in _values)
        {
            Produced++;
            yield return value;
        }
    }

    // The non-generic overload is required by IEnumerable and simply defers.
    IEnumerator IEnumerable.GetEnumerator() => GetEnumerator();
}
