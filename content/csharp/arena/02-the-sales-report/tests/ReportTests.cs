using Learnbox;
using Lesson;

public class ReportTests
{
    private static readonly Sale[] Quarter =
    {
        new("north", "tea", 10m),
        new("south", "tea", 4m),
        new("north", "coffee", 20m),
        new("south", "coffee", 8.50m),
    };

    private static readonly Sale[] None = Array.Empty<Sale>();

    [Test]
    public void TotalsAreAddedPerRegion() =>
        Assert.Sequence(new[] { ("north", 30m), ("south", 12.50m) }, Report.TotalsByRegion(Quarter));

    [Test]
    public void TheLargestTotalComesFirst()
    {
        var sales = new Sale[] { new("east", "tea", 1m), new("west", "tea", 5m), new("east", "tea", 2m) };
        Assert.Sequence(new[] { ("west", 5m), ("east", 3m) }, Report.TotalsByRegion(sales));
    }

    [Test]
    public void LevelRegionsGoAlphabetically()
    {
        var sales = new Sale[] { new("west", "tea", 5m), new("east", "tea", 5m), new("north", "tea", 9m), new("alps", "tea", 5m) };
        Assert.Sequence(new[] { ("north", 9m), ("alps", 5m), ("east", 5m), ("west", 5m) }, Report.TotalsByRegion(sales));
    }

    [Test]
    public void NoSalesNoTotals() =>
        Assert.Equal(0, Report.TotalsByRegion(None).Count);

    [Test]
    public void BestProductIsByTotalNotByCount()
    {
        Assert.Equal("coffee", Report.BestProduct(Quarter));
        var sales = new Sale[] { new("n", "gum", 1m), new("n", "gum", 1m), new("n", "gum", 1m), new("n", "cake", 9m) };
        Assert.Equal("cake", Report.BestProduct(sales));
    }

    [Test]
    public void LevelProductsGoAlphabetically()
    {
        var sales = new Sale[] { new("n", "tea", 5m), new("n", "milk", 2m), new("s", "milk", 3m) };
        Assert.Equal("milk", Report.BestProduct(sales));
    }

    [Test]
    public void NoSalesNoBestProduct() =>
        Assert.Null(Report.BestProduct(None));

    [Test]
    public void Averages()
    {
        var averages = Report.AverageByProduct(Quarter);
        Assert.Equal(2, averages.Count);
        Assert.Equal(7m, averages["tea"]);
        Assert.Equal(14.25m, averages["coffee"]);
    }

    [Test]
    public void AveragesAreRoundedToTwoDecimals()
    {
        var sales = new Sale[] { new("n", "tea", 1m), new("n", "tea", 1m), new("n", "tea", 2m) };
        Assert.Equal(1.33m, Report.AverageByProduct(sales)["tea"]);
    }

    [Test]
    public void NoSalesNoAverages() =>
        Assert.Equal(0, Report.AverageByProduct(None).Count);

    [Test]
    public void TheSalesAreReadOnlyOnce()
    {
        // A generator can only be walked once; ToList it if you need two passes.
        IEnumerable<Sale> Once()
        {
            yield return new Sale("north", "tea", 10m);
            yield return new Sale("north", "tea", 5m);
        }
        Assert.Sequence(new[] { ("north", 15m) }, Report.TotalsByRegion(Once()));
        Assert.Equal("tea", Report.BestProduct(Once()));
    }
}
