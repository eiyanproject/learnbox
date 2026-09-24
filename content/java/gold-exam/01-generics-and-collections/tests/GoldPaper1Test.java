import static org.junit.jupiter.api.Assertions.*;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import org.junit.jupiter.api.Test;

class GoldPaper1Test {

    @Test
    void copyMovesEveryElement() {
        List<Object> dst = new ArrayList<>();
        GoldPaper1.copy(List.of(1, 2, 3), dst);
        assertEquals(List.of(1, 2, 3), dst);
    }

    @Test
    void copyAcceptsAWiderDestination() {
        // ? super Integer means an Object list is a legal destination.
        List<Object> dst = new ArrayList<>();
        GoldPaper1.<Integer>copy(List.of(1), dst);
        assertEquals(1, dst.get(0));
    }

    @Test
    void copyAppendsRatherThanReplaces() {
        List<Object> dst = new ArrayList<>(List.of("x"));
        GoldPaper1.copy(List.of("y"), dst);
        assertEquals(List.of("x", "y"), dst);
    }

    @Test
    void pairHoldsBothValues() {
        GoldPaper1.Pair<String, Integer> p = new GoldPaper1.Pair<>("a", 1);
        assertEquals("a", p.getFirst());
        assertEquals(1, p.getSecond());
    }

    @Test
    void equalPairsAreEqual() {
        assertEquals(new GoldPaper1.Pair<>("a", 1), new GoldPaper1.Pair<>("a", 1));
    }

    @Test
    void differentPairsAreNotEqual() {
        assertNotEquals(new GoldPaper1.Pair<>("a", 1), new GoldPaper1.Pair<>("a", 2));
        assertNotEquals(new GoldPaper1.Pair<>("a", 1), "not a pair");
    }

    @Test
    void equalPairsShareAHashCode() {
        assertEquals(new GoldPaper1.Pair<>("a", 1).hashCode(),
                new GoldPaper1.Pair<>("a", 1).hashCode(),
                "equal objects must have equal hash codes");
    }

    @Test
    void pairsWorkAsSetMembers() {
        // This is what the contract is actually for.
        Set<GoldPaper1.Pair<String, Integer>> set = new HashSet<>();
        set.add(new GoldPaper1.Pair<>("a", 1));
        assertTrue(set.contains(new GoldPaper1.Pair<>("a", 1)),
                "a broken hashCode makes the element unfindable");
        set.add(new GoldPaper1.Pair<>("a", 1));
        assertEquals(1, set.size(), "duplicates should collapse");
    }

    @Test
    void frequencyCounts() {
        assertEquals(Map.of("a", 2, "b", 1), GoldPaper1.frequency(List.of("a", "b", "a")));
    }

    @Test
    void frequencyOfEmptyIsEmpty() {
        assertTrue(GoldPaper1.frequency(List.of()).isEmpty());
    }

    @Test
    void intersectionKeepsCommonItems() {
        assertEquals(List.of(2, 3), GoldPaper1.intersection(List.of(1, 2, 3), List.of(3, 2, 9)));
    }

    @Test
    void intersectionRemovesDuplicates() {
        assertEquals(List.of(1), GoldPaper1.intersection(List.of(1, 1), List.of(1)));
    }

    @Test
    void disjointListsIntersectToNothing() {
        assertEquals(List.of(), GoldPaper1.intersection(List.of(1), List.of(2)));
    }
}
