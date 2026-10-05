import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

class RomanTest {

    @Test
    void singleSymbols() {
        assertEquals("I", Roman.toRoman(1));
        assertEquals("V", Roman.toRoman(5));
        assertEquals("X", Roman.toRoman(10));
        assertEquals("L", Roman.toRoman(50));
        assertEquals("C", Roman.toRoman(100));
        assertEquals("D", Roman.toRoman(500));
        assertEquals("M", Roman.toRoman(1000));
    }

    @Test
    void addingUp() {
        assertEquals("III", Roman.toRoman(3));
        assertEquals("VIII", Roman.toRoman(8));
        assertEquals("MDCLXVI", Roman.toRoman(1666));
    }

    @Test
    void subtractivePairs() {
        assertEquals("IV", Roman.toRoman(4));
        assertEquals("IX", Roman.toRoman(9));
        assertEquals("XL", Roman.toRoman(40));
        assertEquals("XC", Roman.toRoman(90));
        assertEquals("CD", Roman.toRoman(400));
        assertEquals("CM", Roman.toRoman(900));
    }

    @Test
    void mixed() {
        assertEquals("XLIX", Roman.toRoman(49));
        assertEquals("MCMXCIV", Roman.toRoman(1994));
        assertEquals("MMXXIV", Roman.toRoman(2024));
        assertEquals("MMMCMXCIX", Roman.toRoman(3999));
        assertEquals("CDXLIV", Roman.toRoman(444));
    }

    @Test
    void outOfRange() {
        assertThrows(IllegalArgumentException.class, () -> Roman.toRoman(0));
        assertThrows(IllegalArgumentException.class, () -> Roman.toRoman(-5));
        assertThrows(IllegalArgumentException.class, () -> Roman.toRoman(4000));
    }

    @Test
    void readingBack() {
        assertEquals(1, Roman.fromRoman("I"));
        assertEquals(8, Roman.fromRoman("VIII"));
        assertEquals(49, Roman.fromRoman("XLIX"));
        assertEquals(1994, Roman.fromRoman("MCMXCIV"));
        assertEquals(3999, Roman.fromRoman("MMMCMXCIX"));
    }

    @Test
    void readingThePairs() {
        assertEquals(4, Roman.fromRoman("IV"));
        assertEquals(9, Roman.fromRoman("IX"));
        assertEquals(40, Roman.fromRoman("XL"));
        assertEquals(90, Roman.fromRoman("XC"));
        assertEquals(400, Roman.fromRoman("CD"));
        assertEquals(900, Roman.fromRoman("CM"));
    }

    @Test
    void everyNumberSurvivesTheRoundTrip() {
        for (int n = 1; n <= 3999; n++) {
            assertEquals(n, Roman.fromRoman(Roman.toRoman(n)), "round trip of " + n);
        }
    }

    @Test
    void neverFourOfTheSameSymbol() {
        for (int n = 1; n <= 3999; n++) {
            String r = Roman.toRoman(n);
            assertFalse(r.matches(".*(.)\\1{3}.*"), n + " came out as " + r);
        }
    }
}
