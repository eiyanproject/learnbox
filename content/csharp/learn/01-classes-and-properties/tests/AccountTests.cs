using Learnbox;
using Lesson;

public class AccountTests
{
    [Test]
    public void OpensWithZeroByDefault() => Assert.Equal(0m, new Account("ada").Balance);

    [Test]
    public void OpensWithAGivenBalance() => Assert.Equal(50m, new Account("ada", 50).Balance);

    [Test]
    public void KeepsTheOwner() => Assert.Equal("ada", new Account("ada").Owner);

    [Test]
    public void RejectsABlankOwner() =>
        Assert.Throws<ArgumentException>(() => new Account("  "));

    [Test]
    public void DepositAdds()
    {
        var a = new Account("ada");
        a.Deposit(30);
        a.Deposit(20);
        Assert.Equal(50m, a.Balance);
    }

    [Test]
    public void DepositRejectsNonPositive()
    {
        var a = new Account("ada");
        Assert.Throws<ArgumentOutOfRangeException>(() => a.Deposit(0));
        Assert.Throws<ArgumentOutOfRangeException>(() => a.Deposit(-1));
    }

    [Test]
    public void WithdrawSubtracts()
    {
        var a = new Account("ada", 100);
        a.Withdraw(40);
        Assert.Equal(60m, a.Balance);
    }

    [Test]
    public void WithdrawRefusesToOverdraw()
    {
        var a = new Account("ada", 10);
        Assert.Throws<InvalidOperationException>(() => a.Withdraw(11));
        Assert.Equal(10m, a.Balance, "a refused withdrawal must not change the balance");
    }

    [Test]
    public void DecimalKeepsCentsExactly()
    {
        // With double, 0.1 + 0.2 would not be 0.3.
        var a = new Account("ada");
        a.Deposit(0.1m);
        a.Deposit(0.2m);
        Assert.Equal(0.3m, a.Balance);
    }

    [Test]
    public void AsMoneyCarriesTheBalance()
    {
        var m = new Account("ada", 25).AsMoney();
        Assert.Equal(25m, m.Amount);
        Assert.Equal("EUR", m.Currency);
    }

    [Test]
    public void RecordsCompareByValue() =>
        Assert.Equal(new Money(5m, "EUR"), new Money(5m, "EUR"));

    [Test]
    public void DifferentRecordsAreNotEqual() =>
        Assert.NotEqual(new Money(5m, "EUR"), new Money(5m, "USD"));
}
