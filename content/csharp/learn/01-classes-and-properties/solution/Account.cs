namespace Lesson;

public record Money(decimal Amount, string Currency);

public class Account
{
    public string Owner { get; }

    // Readable everywhere, writable only in here: the invariants below are
    // worth nothing if a caller can assign the balance directly.
    public decimal Balance { get; private set; }

    public Account(string owner, decimal opening = 0)
    {
        if (string.IsNullOrWhiteSpace(owner))
        {
            throw new ArgumentException("owner must not be blank", nameof(owner));
        }
        Owner = owner;
        Balance = opening;
    }

    public void Deposit(decimal amount)
    {
        if (amount <= 0)
        {
            throw new ArgumentOutOfRangeException(nameof(amount), "deposit must be positive");
        }
        Balance += amount;
    }

    public void Withdraw(decimal amount)
    {
        if (amount <= 0)
        {
            throw new ArgumentOutOfRangeException(nameof(amount), "withdrawal must be positive");
        }
        if (amount > Balance)
        {
            throw new InvalidOperationException("insufficient funds");
        }
        Balance -= amount;
    }

    public Money AsMoney() => new Money(Balance, "EUR");
}
