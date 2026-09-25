namespace Lesson;

public static class Work
{
    public static async Task<int> DoubleAsync(int n)
    {
        await Task.Delay(1);
        return n * 2;
    }

    public static async Task<int> SumAllAsync(IEnumerable<int> values)
    {
        // Start everything first, then wait once. Awaiting inside the loop
        // would be async but strictly sequential.
        List<Task<int>> tasks = values.Select(DoubleAsync).ToList();
        int[] results = await Task.WhenAll(tasks);
        return results.Sum();
    }

    public static async Task<int> FailAsync()
    {
        await Task.Yield();
        throw new InvalidOperationException("boom");
    }

    public static async Task<int?> TryRunAsync(Func<Task<int>> work)
    {
        try
        {
            // Awaiting rethrows the original exception; blocking on .Result
            // would hand back an AggregateException wrapping it instead.
            return await work();
        }
        catch (InvalidOperationException)
        {
            return null;
        }
    }

    public static async Task<int> CountUpAsync(int upTo, CancellationToken token)
    {
        int count = 0;
        for (int i = 0; i < upTo; i++)
        {
            // Cancellation is cooperative: nothing interrupts us, so we check.
            token.ThrowIfCancellationRequested();
            await Task.Yield();
            count++;
        }
        return count;
    }
}
