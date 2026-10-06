namespace Lesson;

public record Sale(string Region, string Product, decimal Amount);

public static class Report
{
    public static List<(string Region, decimal Total)> TotalsByRegion(IEnumerable<Sale> sales) =>
        sales.GroupBy(s => s.Region)
            .Select(g => (Region: g.Key, Total: g.Sum(s => s.Amount)))
            .OrderByDescending(t => t.Total)
            .ThenBy(t => t.Region, StringComparer.Ordinal)
            .ToList();

    public static string? BestProduct(IEnumerable<Sale> sales) =>
        sales.GroupBy(s => s.Product)
            .OrderByDescending(g => g.Sum(s => s.Amount))
            .ThenBy(g => g.Key, StringComparer.Ordinal)
            .Select(g => g.Key)
            .FirstOrDefault();

    public static Dictionary<string, decimal> AverageByProduct(IEnumerable<Sale> sales) =>
        sales.GroupBy(s => s.Product)
            .ToDictionary(g => g.Key, g => Math.Round(g.Average(s => s.Amount), 2));
}
