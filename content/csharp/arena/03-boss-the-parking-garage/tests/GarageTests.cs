using Learnbox;
using Lesson;

public class GarageTests
{
    private static readonly DateTime Nine = new(2026, 3, 4, 9, 0, 0);

    private static decimal FeeFor(double minutes)
    {
        var garage = new Garage(1);
        garage.Park("AB-123", Nine);
        return garage.Leave("AB-123", Nine.AddMinutes(minutes));
    }

    [Test]
    public void StartsEmpty()
    {
        var garage = new Garage(3);
        Assert.Equal(3, garage.Free);
        Assert.Equal(0, garage.Plates.Count);
        Assert.Equal(0m, garage.Takings);
        Assert.False(garage.IsParked("AB-123"));
    }

    [Test]
    public void ACapacityBelowOneIsRefused()
    {
        Assert.Throws<ArgumentOutOfRangeException>(() => new Garage(0));
        Assert.Throws<ArgumentOutOfRangeException>(() => new Garage(-2));
    }

    [Test]
    public void CarsFillTheLowestSlots()
    {
        var garage = new Garage(3);
        Assert.Equal(1, garage.Park("A", Nine));
        Assert.Equal(2, garage.Park("B", Nine));
        Assert.Equal(3, garage.Park("C", Nine));
        Assert.Equal(0, garage.Free);
    }

    [Test]
    public void AFreedSlotIsReusedLowestFirst()
    {
        var garage = new Garage(3);
        garage.Park("A", Nine);
        garage.Park("B", Nine);
        garage.Park("C", Nine);
        garage.Leave("B", Nine.AddMinutes(5));
        garage.Leave("A", Nine.AddMinutes(5));
        Assert.Equal(1, garage.Park("D", Nine.AddMinutes(10)));
        Assert.Equal(2, garage.Park("E", Nine.AddMinutes(10)));
    }

    [Test]
    public void PlatesAreTidied()
    {
        var garage = new Garage(2);
        garage.Park(" ab-123 ", Nine);
        Assert.True(garage.IsParked("AB-123"));
        Assert.True(garage.IsParked("ab-123"));
        Assert.Sequence(new[] { "AB-123" }, garage.Plates);
        Assert.Equal(0m, garage.Leave("Ab-123", Nine.AddMinutes(1)));
        Assert.False(garage.IsParked("AB-123"));
    }

    [Test]
    public void PlatesComeBackSorted()
    {
        var garage = new Garage(3);
        garage.Park("zz-1", Nine);
        garage.Park("AA-9", Nine);
        garage.Park("mm-5", Nine);
        Assert.Sequence(new[] { "AA-9", "MM-5", "ZZ-1" }, garage.Plates);
    }

    [Test]
    public void ABlankPlateIsRefusedEverywhere()
    {
        var garage = new Garage(2);
        Assert.Throws<ArgumentException>(() => garage.Park("", Nine));
        Assert.Throws<ArgumentException>(() => garage.Park("   ", Nine));
        Assert.Throws<ArgumentException>(() => garage.Leave(" ", Nine));
        Assert.Throws<ArgumentException>(() => garage.IsParked(""));
        Assert.Equal(2, garage.Free);
    }

    [Test]
    public void TheSameCarCannotParkTwice()
    {
        var garage = new Garage(2);
        garage.Park("AB-123", Nine);
        Assert.Throws<InvalidOperationException>(() => garage.Park("ab-123", Nine));
        Assert.Equal(1, garage.Free);
    }

    [Test]
    public void AFullGarageTurnsCarsAway()
    {
        var garage = new Garage(1);
        garage.Park("A", Nine);
        Assert.Throws<InvalidOperationException>(() => garage.Park("B", Nine));
        Assert.False(garage.IsParked("B"));
        garage.Leave("A", Nine.AddMinutes(1));
        Assert.Equal(1, garage.Park("B", Nine.AddMinutes(2)));
    }

    [Test]
    public void ACarThatIsNotInsideCannotLeave()
    {
        var garage = new Garage(1);
        Assert.Throws<KeyNotFoundException>(() => garage.Leave("GHOST", Nine));
        garage.Park("A", Nine);
        garage.Leave("A", Nine.AddMinutes(1));
        Assert.Throws<KeyNotFoundException>(() => garage.Leave("A", Nine.AddMinutes(2)));
    }

    [Test]
    public void LeavingBeforeArrivingIsRefusedAndTheCarStays()
    {
        var garage = new Garage(1);
        garage.Park("A", Nine);
        Assert.Throws<ArgumentException>(() => garage.Leave("A", Nine.AddMinutes(-1)));
        Assert.True(garage.IsParked("A"));
        Assert.Equal(0, garage.Free);
        Assert.Equal(0m, garage.Takings);
    }

    [Test]
    public void TheFirstHalfHourIsFree()
    {
        Assert.Equal(0m, FeeFor(0));
        Assert.Equal(0m, FeeFor(29));
        Assert.Equal(0m, FeeFor(30));
    }

    [Test]
    public void EveryHourStartedCostsTwo()
    {
        Assert.Equal(2m, FeeFor(31));
        Assert.Equal(2m, FeeFor(60));
        Assert.Equal(4m, FeeFor(61));
        Assert.Equal(4m, FeeFor(120));
        Assert.Equal(6m, FeeFor(121));
        Assert.Equal(18m, FeeFor(540));
    }

    [Test]
    public void TheFeeIsCappedAtTwenty()
    {
        Assert.Equal(20m, FeeFor(541));
        Assert.Equal(20m, FeeFor(600));
        Assert.Equal(20m, FeeFor(3 * 24 * 60));
    }

    [Test]
    public void TakingsAddUp()
    {
        var garage = new Garage(3);
        garage.Park("A", Nine);
        garage.Park("B", Nine);
        garage.Park("C", Nine);
        garage.Leave("A", Nine.AddMinutes(10));
        garage.Leave("B", Nine.AddMinutes(61));
        garage.Leave("C", Nine.AddHours(12));
        Assert.Equal(24m, garage.Takings);
        Assert.Equal(3, garage.Free);
    }

    [Test]
    public void TwoGaragesDoNotShare()
    {
        var a = new Garage(1);
        var b = new Garage(1);
        a.Park("A", Nine);
        Assert.False(b.IsParked("A"));
        Assert.Equal(1, b.Free);
    }
}
