namespace Lesson;

public static class Store
{
    public static Dictionary<string, int> CountWords(string text)
    {
        var counts = new Dictionary<string, int>();
        foreach (var word in text.ToLowerInvariant()
                     .Split((char[]?)null, StringSplitOptions.RemoveEmptyEntries))
        {
            counts[word] = counts.GetValueOrDefault(word) + 1;
        }
        return counts;
    }

    public static string? FirstDuplicate(IEnumerable<string> items)
    {
        var seen = new HashSet<string>();
        foreach (var item in items)
        {
            // Add returns false when the item was already there, which saves
            // the second lookup a Contains-then-Add would cost.
            if (!seen.Add(item))
            {
                return item;
            }
        }
        return null;
    }

    public static List<T> Dedupe<T>(IEnumerable<T> items)
    {
        var seen = new HashSet<T>();
        var result = new List<T>();
        foreach (var item in items)
        {
            if (seen.Add(item))
            {
                result.Add(item);
            }
        }
        return result;
    }

    public static List<KeyValuePair<string, int>> TopWords(string text, int n)
    {
        return CountWords(text)
            .OrderByDescending(pair => pair.Value)
            .ThenBy(pair => pair.Key, StringComparer.Ordinal)
            .Take(n)
            .ToList();
    }
}
