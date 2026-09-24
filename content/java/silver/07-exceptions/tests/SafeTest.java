import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

class SafeTest {

    @Test
    void parsesAValidNumber() {
        assertEquals(42, Safe.parseOrDefault("42", -1));
    }

    @Test
    void fallsBackOnRubbish() {
        assertEquals(-1, Safe.parseOrDefault("twelve", -1));
    }

    @Test
    void fallsBackOnNullAndEmpty() {
        assertEquals(0, Safe.parseOrDefault("", 0));
        assertEquals(0, Safe.parseOrDefault(null, 0));
    }

    @Test
    void divides() {
        assertEquals(3, Safe.divide(7, 2), "integer division truncates");
    }

    @Test
    void divideByZeroThrows() {
        assertThrows(ArithmeticException.class, () -> Safe.divide(1, 0));
    }

    @Test
    void describeReturnsOkWhenNothingIsThrown() {
        assertEquals("ok", Safe.describe(() -> {}));
    }

    @Test
    void describeCatchesTheSpecificTypeFirst() {
        assertEquals("bad argument", Safe.describe(() -> {
            throw new IllegalArgumentException("no");
        }));
    }

    @Test
    void describeFallsBackForOtherExceptions() {
        assertEquals("failed", Safe.describe(() -> {
            throw new IllegalStateException("no");
        }));
    }

    @Test
    void numberFormatExceptionIsAnIllegalArgumentException() {
        // NumberFormatException extends IllegalArgumentException, so the
        // narrower catch wins - which is why order matters.
        assertEquals("bad argument", Safe.describe(() -> Integer.parseInt("x")));
    }

    @Test
    void resourcesCloseInReverseOrderOfDeclaration() {
        assertEquals("B,A", Safe.closeOrder(),
                "try-with-resources closes the last declared resource first");
    }
}
