using Learnbox;
using Lesson;

public class StoreTests
{
    [Test]
    public void CountsWords()
    {
        var counts = Store.CountWords("the cat the dog");
        Assert.Equal(2, counts["the"]);
        Assert.Equal(1, counts["cat"]);
    }

    [Test]
    public void CountingIsCaseInsensitive() =>
        Assert.Equal(3, Store.CountWords("The the THE")["the"]);

    [Test]
    public void CountingIgnoresExtraWhitespace() =>
        Assert.Equal(2, Store.CountWords("  a   b  ").Count);

    [Test]
    public void CountingAnEmptyString() =>
        Assert.Equal(0, Store.CountWords("").Count);

    [Test]
    public void FindsTheFirstDuplicate() =>
        Assert.Equal("b", Store.FirstDuplicate(new[] { "a", "b", "c", "b", "a" }));

    [Test]
    public void NoDuplicateReturnsNull() =>
        Assert.Null(Store.FirstDuplicate(new[] { "a", "b" }));

    [Test]
    public void FirstDuplicateOfAnEmptySequence() =>
        Assert.Null(Store.FirstDuplicate(Array.Empty<string>()));

    [Test]
    public void DedupeKeepsFirstSeenOrder() =>
        Assert.Sequence(new[] { "b", "a", "c" },
            Store.Dedupe(new[] { "b", "a", "b", "c", "a" }));

    [Test]
    public void DedupeWorksForAnyType() =>
        Assert.Sequence(new[] { 1, 2 }, Store.Dedupe(new[] { 1, 1, 2, 2 }));

    [Test]
    public void DedupeOfNothing() =>
        Assert.Equal(0, Store.Dedupe(Array.Empty<int>()).Count);

    [Test]
    public void TopWordsOrdersByCount()
    {
        var top = Store.TopWords("a b b c c c", 2);
        Assert.Equal("c", top[0].Key);
        Assert.Equal("b", top[1].Key);
    }

    [Test]
    public void TopWordsBreaksTiesAlphabetically()
    {
        var top = Store.TopWords("zebra zebra apple apple", 2);
        Assert.Equal("apple", top[0].Key);
    }

    [Test]
    public void TopWordsRespectsTheLimit() =>
        Assert.Equal(1, Store.TopWords("a b c", 1).Count);
}
