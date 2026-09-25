using Learnbox;
using Lesson;

public class StoreTests
{
    private static Repository<Item> Seeded()
    {
        var repo = new Repository<Item>();
        repo.Add(new Item(2, "belt", 9.50m));
        repo.Add(new Item(1, "apple", 1.25m));
        repo.Add(new Item(3, "clock", 40m));
        return repo;
    }

    [Test]
    public void ANewRepositoryIsEmpty() => Assert.Equal(0, new Repository<Item>().Count);

    [Test]
    public void AddingCountsUp() => Assert.Equal(3, Seeded().Count);

    [Test]
    public void AddingTheSameIdReplaces()
    {
        var repo = Seeded();
        repo.Add(new Item(1, "apricot", 2m));
        Assert.Equal(3, repo.Count);
        repo.TryGet(1, out var item);
        Assert.Equal("apricot", item!.Name);
    }

    [Test]
    public void TryGetFindsAnItem()
    {
        Assert.True(Seeded().TryGet(2, out var item));
        Assert.Equal("belt", item!.Name);
    }

    [Test]
    public void TryGetReportsAMissWithoutThrowing()
    {
        Assert.False(Seeded().TryGet(99, out var item));
        Assert.Null(item);
    }

    [Test]
    public void RemoveReportsWhetherItRemovedAnything()
    {
        var repo = Seeded();
        Assert.True(repo.Remove(1));
        Assert.False(repo.Remove(1));
        Assert.Equal(2, repo.Count);
    }

    [Test]
    public void AllComesBackOrderedById() =>
        Assert.Sequence(new[] { 1, 2, 3 }, Seeded().All().Select(i => i.Id));

    [Test]
    public void AllOfAnEmptyRepository() =>
        Assert.Equal(0, new Repository<Item>().All().Count());

    [Test]
    public void TheItemSatisfiesTheInterface()
    {
        IIdentified item = new Item(7, "x", 0m);
        Assert.Equal(7, item.Id);
    }

    [Test]
    public void LargestOfStrings() =>
        Assert.Equal("pear", Extremes.Largest(new[] { "apple", "pear", "fig" }));

    [Test]
    public void LargestOfOne() =>
        Assert.Equal("only", Extremes.Largest(new[] { "only" }));

    [Test]
    public void LargestOfNothingIsNull() =>
        Assert.Null(Extremes.Largest(Array.Empty<string>()));

    [Test]
    public void TheRepositoryIsGenericOverAnythingIdentified()
    {
        // Nothing in Repository mentions Item - the constraint is the contract.
        var repo = new Repository<Item>();
        repo.Add(new Item(5, "e", 1m));
        Assert.Equal(1, repo.Count);
    }
}
