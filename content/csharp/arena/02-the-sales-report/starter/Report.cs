namespace Lesson;

public record Sale(string Region, string Product, decimal Amount);

public static class Report
{
    public static List<(string Region, decimal Total)> TotalsByRegion(IEnumerable<Sale> sales)
    {
        throw new NotImplementedException();
    }

    public static string? BestProduct(IEnumerable<Sale> sales)
    {
        throw new NotImplementedException();
    }

    public static Dictionary<string, decimal> AverageByProduct(IEnumerable<Sale> sales)
    {
        throw new NotImplementedException();
    }
}
