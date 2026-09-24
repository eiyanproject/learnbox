import static org.junit.jupiter.api.Assertions.*;

import java.util.Map;
import java.util.NoSuchElementException;
import java.util.Optional;
import org.junit.jupiter.api.Test;

class MaybeTest {

    private static final Map<String, String> PEOPLE = Map.of("a", "ada", "g", "grace");

    @Test
    void findReturnsThePresentValue() {
        assertEquals(Optional.of("ada"), Maybe.find(PEOPLE, "a"));
    }

    @Test
    void findOnAMissingKeyIsEmptyNotNull() {
        Optional<String> result = Maybe.find(PEOPLE, "zz");
        assertNotNull(result, "never return null from a method returning Optional");
        assertTrue(result.isEmpty());
    }

    @Test
    void nameLengthOfAPresentValue() {
        assertEquals(3, Maybe.nameLength(PEOPLE, "a"));
        assertEquals(5, Maybe.nameLength(PEOPLE, "g"));
    }

    @Test
    void nameLengthFallsBackWhenMissing() {
        assertEquals(-1, Maybe.nameLength(PEOPLE, "zz"));
    }

    @Test
    void firstNonBlankPrefersTheFirst() {
        assertEquals(Optional.of("a"),
                Maybe.firstNonBlank(Optional.of("a"), Optional.of("b")));
    }

    @Test
    void firstNonBlankSkipsAnEmptyOptional() {
        assertEquals(Optional.of("b"), Maybe.firstNonBlank(Optional.empty(), Optional.of("b")));
    }

    @Test
    void firstNonBlankSkipsABlankString() {
        assertEquals(Optional.of("b"), Maybe.firstNonBlank(Optional.of("   "), Optional.of("b")));
    }

    @Test
    void firstNonBlankOfTwoEmpties() {
        assertTrue(Maybe.firstNonBlank(Optional.empty(), Optional.empty()).isEmpty());
    }

    @Test
    void requireValueReturnsThePresentValue() {
        assertEquals("ada", Maybe.requireValue(Optional.of("ada")));
    }

    @Test
    void requireValueThrowsWhenEmpty() {
        assertThrows(NoSuchElementException.class, () -> Maybe.requireValue(Optional.empty()));
    }

    @Test
    void orDefault() {
        assertEquals("ada", Maybe.orDefault(Optional.of("ada"), "nobody"));
        assertEquals("nobody", Maybe.orDefault(Optional.empty(), "nobody"));
    }
}
