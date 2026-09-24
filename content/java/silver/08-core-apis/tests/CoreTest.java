import static org.junit.jupiter.api.Assertions.*;

import java.time.LocalDate;
import org.junit.jupiter.api.Test;

class CoreTest {

    @Test
    void boxedEqualsForSmallCachedValues() {
        assertTrue(Core.boxedEquals(127, 127));
    }

    @Test
    void boxedEqualsAboveTheIntegerCache() {
        // == would be false here: only -128..127 are cached.
        assertTrue(Core.boxedEquals(1000, 1000), "compare boxed values with equals, not ==");
    }

    @Test
    void boxedEqualsIsFalseForDifferentValues() {
        assertFalse(Core.boxedEquals(1, 2));
    }

    @Test
    void safeUnboxReturnsTheValue() {
        assertEquals(7, Core.safeUnbox(7, -1));
    }

    @Test
    void safeUnboxHandlesNull() {
        assertEquals(-1, Core.safeUnbox(null, -1),
                "unboxing a null Integer throws NullPointerException");
    }

    @Test
    void daysBetweenCountsForward() {
        assertEquals(10, Core.daysBetween(LocalDate.of(2026, 9, 1), LocalDate.of(2026, 9, 11)));
    }

    @Test
    void daysBetweenIsNegativeGoingBackwards() {
        assertEquals(-10, Core.daysBetween(LocalDate.of(2026, 9, 11), LocalDate.of(2026, 9, 1)));
    }

    @Test
    void daysBetweenAcrossAMonth() {
        assertEquals(31, Core.daysBetween(LocalDate.of(2026, 1, 1), LocalDate.of(2026, 2, 1)));
    }

    @Test
    void addWeeksReturnsANewDate() {
        LocalDate start = LocalDate.of(2026, 9, 24);
        assertEquals(LocalDate.of(2026, 10, 8), Core.addWeeks(start, 2));
        assertEquals(LocalDate.of(2026, 9, 24), start, "LocalDate is immutable");
    }

    @Test
    void recordAccessorsHaveNoGetPrefix() {
        Core.Point p = new Core.Point(3, 4);
        assertEquals(3, p.x());
        assertEquals(4, p.y());
    }

    @Test
    void recordEqualityIsByValue() {
        assertEquals(new Core.Point(1, 2), new Core.Point(1, 2),
                "a record gets equals and hashCode for free");
    }

    @Test
    void recordMethod() {
        assertEquals(5.0, new Core.Point(3, 4).distanceFromOrigin(), 0.0001);
    }
}
