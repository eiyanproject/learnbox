using Learnbox;
using Lesson;

public class QueryTests
{
    private static readonly List<Person> People = new()
    {
        new Person("ada", 36, "London"),
        new Person("bob", 17, "Paris"),
        new Person("cat", 22, "London"),
        new Person("dan", 45, "Berlin"),
    };

    [Test]
    public void AdultNamesExcludesMinors() =>
        Assert.Sequence(new[] { "ada", "cat", "dan" }, Query.AdultNames(People));

    [Test]
    public void EighteenIsAnAdult() =>
        Assert.Sequence(new[] { "x" },
            Query.AdultNames(new[] { new Person("x", 18, "A") }));

    [Test]
    public void AdultNamesOfNobody() =>
        Assert.Equal(0, Query.AdultNames(Array.Empty<Person>()).Count);

    [Test]
    public void CountsByCity()
    {
        var counts = Query.CountByCity(People);
        Assert.Equal(2, counts["London"]);
        Assert.Equal(1, counts["Paris"]);
    }

    [Test]
    public void CountByCityOfNobody() =>
        Assert.Equal(0, Query.CountByCity(Array.Empty<Person>()).Count);

    [Test]
    public void AveragesTheAges() => Assert.Near(30.0, Query.AverageAge(People));

    [Test]
    public void AverageOfNobodyIsZero() =>
        Assert.Near(0, Query.AverageAge(Array.Empty<Person>()));

    [Test]
    public void FindsTheOldest() => Assert.Equal("dan", Query.Oldest(People)!.Name);

    [Test]
    public void OldestOfNobodyIsNull() =>
        Assert.Null(Query.Oldest(Array.Empty<Person>()));

    [Test]
    public void CitiesWithAtLeastTwo() =>
        Assert.Sequence(new[] { "London" }, Query.CitiesWithAtLeast(People, 2));

    [Test]
    public void CitiesWithAtLeastOneIsAllOfThem() =>
        Assert.Sequence(new[] { "Berlin", "London", "Paris" },
            Query.CitiesWithAtLeast(People, 1));

    [Test]
    public void CitiesWithAnImpossibleThreshold() =>
        Assert.Equal(0, Query.CitiesWithAtLeast(People, 99).Count);

    [Test]
    public void QueriesDoNotModifyTheSource()
    {
        Query.AdultNames(People);
        Assert.Equal(4, People.Count);
    }
}
