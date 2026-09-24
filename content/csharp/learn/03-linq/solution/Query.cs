namespace Lesson;

public record Person(string Name, int Age, string City);

public static class Query
{
    public static List<string> AdultNames(IEnumerable<Person> people) =>
        people.Where(p => p.Age >= 18)
              .OrderBy(p => p.Name, StringComparer.Ordinal)
              .Select(p => p.Name)
              .ToList();

    public static Dictionary<string, int> CountByCity(IEnumerable<Person> people) =>
        people.GroupBy(p => p.City)
              .ToDictionary(g => g.Key, g => g.Count());

    public static double AverageAge(IEnumerable<Person> people)
    {
        // Average() throws on an empty sequence rather than returning zero,
        // because the average of nothing does not exist.
        var list = people.ToList();
        return list.Count == 0 ? 0 : list.Average(p => p.Age);
    }

    public static Person? Oldest(IEnumerable<Person> people) =>
        people.OrderByDescending(p => p.Age).FirstOrDefault();

    public static List<string> CitiesWithAtLeast(IEnumerable<Person> people, int n) =>
        people.GroupBy(p => p.City)
              .Where(g => g.Count() >= n)
              .Select(g => g.Key)
              .OrderBy(city => city, StringComparer.Ordinal)
              .ToList();
}
