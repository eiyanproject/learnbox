using Learnbox;
using Lesson;

public class SafetyTests
{
    [Test]
    public void DisplayTrimsAName() => Assert.Equal("ada", Safety.Display("  ada  "));

    [Test]
    public void DisplayHandlesNull() => Assert.Equal("anonymous", Safety.Display(null));

    [Test]
    public void DisplayHandlesWhitespaceOnly() => Assert.Equal("anonymous", Safety.Display("   "));

    [Test]
    public void LengthOfNullIsZero() => Assert.Equal(0, Safety.Length(null));

    [Test]
    public void LengthOfAString() => Assert.Equal(3, Safety.Length("abc"));

    [Test]
    public void TryParseAgeAcceptsANumber()
    {
        Assert.True(Safety.TryParseAge(" 42 ", out int age));
        Assert.Equal(42, age);
    }

    [Test]
    public void TryParseAgeAcceptsTheBoundaries()
    {
        Assert.True(Safety.TryParseAge("0", out int low));
        Assert.Equal(0, low);
        Assert.True(Safety.TryParseAge("150", out int high));
        Assert.Equal(150, high);
    }

    [Test]
    public void TryParseAgeRejectsOutOfRange()
    {
        Assert.False(Safety.TryParseAge("151", out int age));
        Assert.Equal(0, age);
        Assert.False(Safety.TryParseAge("-1", out _));
    }

    [Test]
    public void TryParseAgeRejectsNonsenseWithoutThrowing()
    {
        Assert.False(Safety.TryParseAge("old", out int age));
        Assert.Equal(0, age);
        Assert.False(Safety.TryParseAge(null, out _));
        Assert.False(Safety.TryParseAge("", out _));
    }

    [Test]
    public void ANewAccountStartsWhereItWasOpened()
    {
        Assert.Equal(0m, new Account().Balance);
        Assert.Equal(25m, new Account(25m).Balance);
    }

    [Test]
    public void OpeningOverdrawnIsRejected() =>
        Assert.Throws<ArgumentOutOfRangeException>(() => new Account(-1m));

    [Test]
    public void DepositAndWithdrawMoveTheBalance()
    {
        var account = new Account();
        account.Deposit(100m);
        account.Withdraw(30m);
        Assert.Equal(70m, account.Balance);
    }

    [Test]
    public void ANonPositiveAmountThrows()
    {
        var account = new Account(10m);
        Assert.Throws<ArgumentOutOfRangeException>(() => account.Deposit(0m));
        Assert.Throws<ArgumentOutOfRangeException>(() => account.Withdraw(-5m));
    }

    [Test]
    public void AnOverdraftIsAnInvalidOperationNotABadArgument()
    {
        var account = new Account(10m);
        Assert.Throws<InvalidOperationException>(() => account.Withdraw(11m));
    }

    [Test]
    public void AFailedWithdrawalLeavesTheBalanceAlone()
    {
        var account = new Account(10m);
        try
        {
            account.Withdraw(999m);
        }
        catch (InvalidOperationException)
        {
            // expected
        }
        Assert.Equal(10m, account.Balance);
    }

    [Test]
    public void WithdrawingEverythingIsAllowed()
    {
        var account = new Account(10m);
        account.Withdraw(10m);
        Assert.Equal(0m, account.Balance);
    }
}
