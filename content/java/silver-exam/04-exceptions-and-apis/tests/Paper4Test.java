import static org.junit.jupiter.api.Assertions.*;

import java.time.DateTimeException;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

class Paper4Test {

    @Test
    void theReturnInFinallyWins() {
        assertEquals(2, Paper4.finallyWins(),
                "a return in finally replaces the one from try");
    }

    @Test
    void classifyNamesTheException() {
        assertEquals("IllegalStateException", Paper4.classify(() -> {
            throw new IllegalStateException();
        }));
    }

    @Test
    void classifyReportsNoneWhenNothingIsThrown() {
        assertEquals("none", Paper4.classify(() -> {}));
    }

    @Test
    void classifyDistinguishesTheSubclass() {
        // NumberFormatException extends IllegalArgumentException, but its own
        // simple name is what should come back.
        assertEquals("NumberFormatException", Paper4.classify(() -> Integer.parseInt("x")));
    }

    @Test
    void classifyCatchesArithmetic() {
        assertEquals("ArithmeticException", Paper4.classify(() -> {
            int unused = 1 / 0;
        }));
    }

    @Test
    void sumsTwoValues() {
        assertEquals(Integer.valueOf(5), Paper4.sumOrNull(2, 3));
    }

    @Test
    void sumWithANullReturnsNull() {
        assertNull(Paper4.sumOrNull(null, 3), "unboxing null would throw");
        assertNull(Paper4.sumOrNull(2, null));
    }

    @Test
    void sumWorksAboveTheIntegerCache() {
        assertEquals(Integer.valueOf(2000), Paper4.sumOrNull(1000, 1000));
    }

    @ParameterizedTest
    @CsvSource({"2024,true", "2000,true", "2023,false", "1900,false", "2026,false"})
    void leapYears(int year, boolean expected) {
        assertEquals(expected, Paper4.isLeap(year));
    }

    @Test
    void monthNames() {
        assertEquals("JANUARY", Paper4.monthName(1));
        assertEquals("DECEMBER", Paper4.monthName(12));
    }

    @Test
    void invalidMonthThrows() {
        assertThrows(DateTimeException.class, () -> Paper4.monthName(13));
        assertThrows(DateTimeException.class, () -> Paper4.monthName(0));
    }
}
