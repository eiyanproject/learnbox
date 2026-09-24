import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

class NumbersTest {

    @Test
    void averageDoesNotTruncate() {
        assertEquals(4.5, Numbers.averageOf(7, 2), 0.0001,
                "7 + 2 = 9, and 9 / 2 is 4.5 - dividing by 2 instead of 2.0 gives 4.0");
    }

    @Test
    void averageOfEvenSum() {
        assertEquals(5.0, Numbers.averageOf(4, 6), 0.0001);
    }

    @Test
    void averageOfNegatives() {
        assertEquals(-2.5, Numbers.averageOf(-2, -3), 0.0001);
    }

    @Test
    void narrowingKeepsSmallValues() {
        assertEquals(42, Numbers.narrow(42L));
    }

    @Test
    void narrowingDiscardsTheHighBits() {
        // 2^32 + 7 truncated into an int is 7: the top bits are simply dropped.
        assertEquals(7, Numbers.narrow(4294967303L));
    }

    @Test
    void overflowWrapsInsteadOfThrowing() {
        assertEquals(Integer.MIN_VALUE, Numbers.overflowed(),
                "Java does not throw on integer overflow - it wraps");
    }

    @Test
    void evenNumbers() {
        assertTrue(Numbers.isEven(0));
        assertTrue(Numbers.isEven(2));
        assertFalse(Numbers.isEven(3));
    }

    @Test
    void evenWorksForNegatives() {
        // -3 % 2 is -1 in Java, so a test against 1 would be wrong here.
        assertTrue(Numbers.isEven(-4));
        assertFalse(Numbers.isEven(-3));
    }

    @Test
    void nextLetterAdvancesTheCharacter() {
        assertEquals('b', Numbers.nextLetter('a'));
        assertEquals('Z', Numbers.nextLetter('Y'));
    }
}
