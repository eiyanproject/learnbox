import static org.junit.jupiter.api.Assertions.*;

import java.util.List;
import java.util.Map;
import java.util.concurrent.Callable;
import org.junit.jupiter.api.Test;

class ConcurrentTest {

    @Test
    void safeCountIsAlwaysExact() {
        assertEquals(40000, Concurrent.safeCount(4, 10000));
    }

    @Test
    void safeCountWithOneThread() {
        assertEquals(100, Concurrent.safeCount(1, 100));
    }

    @Test
    void safeCountWithNoWork() {
        assertEquals(0, Concurrent.safeCount(4, 0));
    }

    @Test
    void racyCountNeverExceedsTheTotal() {
        // It may lose updates, but it cannot invent them.
        int result = Concurrent.racyCount(4, 10000);
        assertTrue(result <= 40000, "increments can be lost, never gained");
        assertTrue(result > 0);
    }

    @Test
    void racyCountIsSingleThreadCorrect() {
        // With one thread there is nothing to race against.
        assertEquals(1000, Concurrent.racyCount(1, 1000));
    }

    @Test
    void runAllReturnsResultsInOrder() throws Exception {
        List<Callable<Integer>> tasks = List.of(() -> 1, () -> 2, () -> 3);
        assertEquals(List.of(1, 2, 3), Concurrent.runAll(tasks));
    }

    @Test
    void runAllActuallyRunsEveryTask() throws Exception {
        List<Callable<Integer>> tasks = List.of(() -> 10, () -> 20);
        assertEquals(30, Concurrent.runAll(tasks).stream().mapToInt(Integer::intValue).sum());
    }

    @Test
    void runAllWithNoTasks() throws Exception {
        assertEquals(List.of(), Concurrent.runAll(List.of()));
    }

    @Test
    void concurrentTallyCounts() {
        Map<String, Integer> counts = Concurrent.concurrentTally(List.of("a", "b", "a"));
        assertEquals(2, counts.get("a"));
        assertEquals(1, counts.get("b"));
    }

    @Test
    void concurrentTallySurvivesAParallelLoad() {
        List<String> many = new java.util.ArrayList<>();
        for (int i = 0; i < 20000; i++) {
            many.add(i % 2 == 0 ? "even" : "odd");
        }
        Map<String, Integer> counts = Concurrent.concurrentTally(many);
        assertEquals(10000, counts.get("even"), "a plain HashMap would lose updates here");
        assertEquals(10000, counts.get("odd"));
    }
}
