namespace Lesson;

public static class Safety
{
    // ?. gives null rather than throwing; ?? supplies the fallback. Note that
    // a name of only spaces trims to empty, which is not null, so it needs its
    // own check.
    public static string Display(string? name)
    {
        string trimmed = name?.Trim() ?? "";
        return trimmed.Length == 0 ? "anonymous" : trimmed;
    }

    public static int Length(string? text) => text?.Length ?? 0;

    // Bad input from a person is a normal outcome, so this is the Try pattern
    // rather than an exception.
    public static bool TryParseAge(string? text, out int age)
    {
        age = 0;
        if (text is null || !int.TryParse(text.Trim(), out int parsed))
        {
            return false;
        }
        if (parsed < 0 || parsed > 150)
        {
            return false;
        }
        age = parsed;
        return true;
    }
}

public class Account
{
    public Account(decimal opening = 0m)
    {
        if (opening < 0)
        {
            throw new ArgumentOutOfRangeException(nameof(opening), "cannot open overdrawn");
        }
        Balance = opening;
    }

    public decimal Balance { get; private set; }

    public void Deposit(decimal amount)
    {
        // A non-positive deposit is a caller bug, not a normal outcome.
        if (amount <= 0)
        {
            throw new ArgumentOutOfRangeException(nameof(amount), "must be positive");
        }
        Balance += amount;
    }

    public void Withdraw(decimal amount)
    {
        if (amount <= 0)
        {
            throw new ArgumentOutOfRangeException(nameof(amount), "must be positive");
        }
        if (amount > Balance)
        {
            throw new InvalidOperationException("insufficient funds");
        }
        Balance -= amount;
    }
}
