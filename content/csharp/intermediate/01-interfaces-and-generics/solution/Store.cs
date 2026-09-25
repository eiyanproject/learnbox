namespace Lesson;

// An interface names a capability. Its members are public by definition, so
// they carry no access modifier here.
public interface IIdentified
{
    int Id { get; }
}

public record Item(int Id, string Name, decimal Price) : IIdentified;

public class Repository<T> where T : class, IIdentified
{
    private readonly Dictionary<int, T> _items = new();

    public int Count => _items.Count;

    /// <summary>Adds or replaces the entry with this Id.</summary>
    public void Add(T item) => _items[item.Id] = item;

    // The framework's Try pattern: failure is ordinary, so it is a return
    // value rather than an exception. The out parameter is assigned on both
    // paths, which the compiler insists on.
    public bool TryGet(int id, out T? item) => _items.TryGetValue(id, out item);

    public bool Remove(int id) => _items.Remove(id);

    public IEnumerable<T> All() => _items.Values.OrderBy(i => i.Id);
}

public static class Extremes
{
    // The constraint is what makes CompareTo available; without it T could be
    // anything and nothing could be called on it.
    public static T? Largest<T>(IEnumerable<T> items) where T : class, IComparable<T>
    {
        T? best = null;
        foreach (T item in items)
        {
            if (best is null || item.CompareTo(best) > 0)
            {
                best = item;
            }
        }
        return best;
    }
}
