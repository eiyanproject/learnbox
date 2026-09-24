import static org.junit.jupiter.api.Assertions.*;

import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;

class BoxesTest {

    @Test
    void boxHoldsAndReturnsAValue() {
        Boxes.Box<String> b = new Boxes.Box<>("hello");
        assertEquals("hello", b.get());
    }

    @Test
    void boxCanBeReassigned() {
        Boxes.Box<Integer> b = new Boxes.Box<>(1);
        b.set(2);
        assertEquals(2, b.get());
    }

    @Test
    void boxWorksForAnyType() {
        assertEquals(List.of(1, 2), new Boxes.Box<>(List.of(1, 2)).get());
    }

    @Test
    void sumAllAcceptsIntegers() {
        assertEquals(6.0, Boxes.sumAll(List.of(1, 2, 3)), 0.0001);
    }

    @Test
    void sumAllAcceptsDoubles() {
        // The same method takes List<Double> because of ? extends Number.
        assertEquals(4.0, Boxes.sumAll(List.of(1.5, 2.5)), 0.0001);
    }

    @Test
    void sumAllOfEmptyIsZero() {
        assertEquals(0.0, Boxes.sumAll(List.of()), 0.0001);
    }

    @Test
    void addNumbersIntoAnIntegerList() {
        List<Integer> target = new ArrayList<>();
        Boxes.addNumbers(target, 3);
        assertEquals(List.of(1, 2, 3), target);
    }

    @Test
    void addNumbersIntoAWiderList() {
        // ? super Integer means an Object list is acceptable too.
        List<Object> target = new ArrayList<>();
        Boxes.addNumbers(target, 2);
        assertEquals(List.of(1, 2), target);
    }

    @Test
    void firstOrDefaultReturnsTheFirst() {
        assertEquals("a", Boxes.firstOrDefault(List.of("a", "b"), "z"));
    }

    @Test
    void firstOrDefaultFallsBack() {
        assertEquals("z", Boxes.firstOrDefault(List.<String>of(), "z"));
    }

    @Test
    void largestOfComparables() {
        assertEquals(9, Boxes.largest(List.of(3, 9, 4)));
        assertEquals("pear", Boxes.largest(List.of("apple", "pear", "fig")));
    }

    @Test
    void largestOfEmptyThrows() {
        assertThrows(IllegalArgumentException.class, () -> Boxes.largest(List.<Integer>of()));
    }
}
