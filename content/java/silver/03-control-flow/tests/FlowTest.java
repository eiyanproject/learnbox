import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

class FlowTest {

    @ParameterizedTest
    @CsvSource({"100,A", "90,A", "89,B", "80,B", "79,C", "70,C", "69,D", "60,D", "59,F", "0,F"})
    void gradeBoundaries(int score, String expected) {
        assertEquals(expected, Flow.grade(score));
    }

    @ParameterizedTest
    @CsvSource({"1,weekday", "5,weekday", "6,weekend", "7,weekend", "0,invalid", "8,invalid"})
    void dayTypes(int day, String expected) {
        assertEquals(expected, Flow.dayType(day));
    }

    @Test
    void firstMultipleFindsIt() {
        assertEquals(4, Flow.firstMultiple(new int[] {3, 4, 6}, 2));
    }

    @Test
    void firstMultipleReturnsTheFirstNotTheSmallest() {
        assertEquals(6, Flow.firstMultiple(new int[] {6, 4}, 2));
    }

    @Test
    void firstMultipleWhenNoneMatch() {
        assertEquals(-1, Flow.firstMultiple(new int[] {1, 3, 5}, 2));
    }

    @Test
    void firstMultipleOfAnEmptyArray() {
        assertEquals(-1, Flow.firstMultiple(new int[] {}, 3));
    }

    @Test
    void countdownFromThree() {
        assertEquals("3,2,1", Flow.countdown(3));
    }

    @Test
    void countdownFromOne() {
        assertEquals("1", Flow.countdown(1));
    }

    @Test
    void countdownHasNoTrailingSeparator() {
        assertFalse(Flow.countdown(5).endsWith(","), "the separator goes between items");
    }

    @Test
    void countdownFromZeroIsEmpty() {
        assertEquals("", Flow.countdown(0));
        assertEquals("", Flow.countdown(-2));
    }
}
