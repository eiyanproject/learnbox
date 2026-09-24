import static org.junit.jupiter.api.Assertions.*;

import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

class GoldPaper2Test {

    @Test
    void averageOfSeveral() {
        assertEquals(4.0, GoldPaper2.averageLength(List.of("ada", "grace")), 0.0001);
    }

    @Test
    void averageOfEmptyIsZeroNotAnException() {
        assertEquals(0.0, GoldPaper2.averageLength(List.of()), 0.0001,
                "average() returns OptionalDouble - do not call getAsDouble on an empty one");
    }

    @Test
    void groupsByFirstLetter() {
        Map<Character, List<String>> grouped =
                GoldPaper2.namesByInitial(List.of("ada", "alan", "grace"));
        assertEquals(List.of("ada", "alan"), grouped.get('a'));
        assertEquals(List.of("grace"), grouped.get('g'));
    }

    @Test
    void groupingAnEmptyListGivesAnEmptyMap() {
        assertTrue(GoldPaper2.namesByInitial(List.of()).isEmpty());
    }

    @Test
    void countsLongerThan() {
        assertEquals(2, GoldPaper2.countLongerThan(List.of("ada", "grace", "alan"), 3));
    }

    @Test
    void countIsStrictlyGreaterThan() {
        assertEquals(0, GoldPaper2.countLongerThan(List.of("abc"), 3));
    }

    @Test
    void summariseShowsEndsAndSize() {
        assertEquals("a..c (3)", GoldPaper2.summarise(List.of("a", "b", "c")));
    }

    @Test
    void summariseOfOneItem() {
        assertEquals("a..a (1)", GoldPaper2.summarise(List.of("a")));
    }

    @Test
    void summariseOfEmpty() {
        assertEquals("none", GoldPaper2.summarise(List.of()));
    }

    @Test
    void topNOrdersByLengthDescending() {
        assertEquals(List.of("grace", "alan"),
                GoldPaper2.topN(List.of("ada", "grace", "alan"), 2));
    }

    @Test
    void topNBreaksTiesAlphabetically() {
        assertEquals(List.of("ada", "bob"), GoldPaper2.topN(List.of("bob", "ada"), 2));
    }

    @Test
    void topNWhenNIsLargerThanTheList() {
        assertEquals(2, GoldPaper2.topN(List.of("a", "b"), 10).size());
    }
}
