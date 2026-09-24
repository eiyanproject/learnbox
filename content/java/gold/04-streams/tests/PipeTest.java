import static org.junit.jupiter.api.Assertions.*;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.Test;

class PipeTest {

    @Test
    void longNamesFiltersThenMaps() {
        assertEquals(List.of("GRACE", "ALAN"), Pipe.longNames(List.of("ada", "grace", "alan"), 3));
    }

    @Test
    void longNamesUsesStrictlyGreaterThan() {
        assertEquals(List.of(), Pipe.longNames(List.of("abc"), 3));
    }

    @Test
    void longNamesOnAnEmptyList() {
        assertEquals(List.of(), Pipe.longNames(List.of(), 1));
    }

    @Test
    void totalSumsTheLengths() {
        assertEquals(12, Pipe.total(List.of("ada", "grace", "alan")));
    }

    @Test
    void totalOfEmptyIsZero() {
        assertEquals(0, Pipe.total(List.of()));
    }

    @Test
    void groupByLength() {
        Map<Integer, List<String>> grouped = Pipe.groupByLength(List.of("ada", "bob", "grace"));
        assertEquals(List.of("ada", "bob"), grouped.get(3));
        assertEquals(List.of("grace"), grouped.get(5));
    }

    @Test
    void groupByLengthHasNoEmptyBuckets() {
        assertFalse(Pipe.groupByLength(List.of("ada")).containsKey(4));
    }

    @Test
    void firstMatchingFindsIt() {
        assertEquals(Optional.of("grace"),
                Pipe.firstMatching(List.of("ada", "grace", "gwen"), s -> s.startsWith("g")));
    }

    @Test
    void firstMatchingReturnsEmptyRatherThanNull() {
        Optional<String> result = Pipe.firstMatching(List.of("ada"), s -> s.startsWith("z"));
        assertNotNull(result, "return the Optional itself, not its contents");
        assertTrue(result.isEmpty());
    }

    @Test
    void joinedWithCommas() {
        assertEquals("a,b,c", Pipe.joined(List.of("a", "b", "c")));
    }

    @Test
    void joinedOfOneAndOfNone() {
        assertEquals("a", Pipe.joined(List.of("a")));
        assertEquals("", Pipe.joined(List.of()));
    }
}
