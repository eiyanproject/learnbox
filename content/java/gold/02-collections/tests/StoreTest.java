import static org.junit.jupiter.api.Assertions.*;

import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

class StoreTest {

    @Test
    void countsWords() {
        assertEquals(Map.of("the", 2, "cat", 1, "dog", 1), Store.countWords("the cat the dog"));
    }

    @Test
    void countingIsCaseInsensitive() {
        assertEquals(Map.of("the", 3), Store.countWords("The the THE"));
    }

    @Test
    void countingIgnoresExtraWhitespace() {
        assertEquals(Map.of("a", 1, "b", 1), Store.countWords("  a   b "));
    }

    @Test
    void countingAnEmptyString() {
        assertTrue(Store.countWords("").isEmpty());
    }

    @Test
    void firstUniqueKeepsInsertionOrder() {
        // "the" repeats, so the first word appearing once is "cat".
        assertEquals("cat", Store.firstUnique("the cat the dog"));
    }

    @Test
    void firstUniqueWhenEverythingRepeats() {
        assertNull(Store.firstUnique("a a b b"));
    }

    @Test
    void sortedByValueOrdersDescending() {
        List<Map.Entry<String, Integer>> sorted =
                Store.sortedByValue(Map.of("a", 1, "b", 5, "c", 3));
        assertEquals("b", sorted.get(0).getKey());
        assertEquals("c", sorted.get(1).getKey());
        assertEquals("a", sorted.get(2).getKey());
    }

    @Test
    void tiesBreakOnTheKey() {
        List<Map.Entry<String, Integer>> sorted =
                Store.sortedByValue(Map.of("zebra", 2, "apple", 2));
        assertEquals("apple", sorted.get(0).getKey(), "equal counts sort by key ascending");
    }

    @Test
    void dedupeKeepsFirstSeenOrder() {
        assertEquals(List.of("b", "a", "c"), Store.dedupe(List.of("b", "a", "b", "c", "a")));
    }

    @Test
    void dedupeOfAnEmptyList() {
        assertEquals(List.of(), Store.dedupe(List.of()));
    }
}
