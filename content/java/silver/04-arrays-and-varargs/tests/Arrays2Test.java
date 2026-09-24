import static org.junit.jupiter.api.Assertions.*;

import java.util.Arrays;
import org.junit.jupiter.api.Test;

class Arrays2Test {

    @Test
    void sumsSeveralValues() {
        assertEquals(6, Arrays2.sum(1, 2, 3));
    }

    @Test
    void sumOfNoArgumentsIsZero() {
        assertEquals(0, Arrays2.sum(), "varargs with no arguments is an empty array, not null");
    }

    @Test
    void sumAcceptsAnArrayDirectly() {
        assertEquals(10, Arrays2.sum(new int[] {1, 2, 3, 4}));
    }

    @Test
    void largestFindsTheMaximum() {
        assertEquals(9, Arrays2.largest(new int[] {3, 9, 4}));
    }

    @Test
    void largestWorksWithNegatives() {
        assertEquals(-2, Arrays2.largest(new int[] {-5, -2, -9}),
                "starting from 0 instead of the first element breaks this case");
    }

    @Test
    void largestOfEmptyThrows() {
        assertThrows(IllegalArgumentException.class, () -> Arrays2.largest(new int[] {}));
    }

    @Test
    void copyWithoutRemovesEveryOccurrence() {
        assertArrayEquals(new int[] {1, 3}, Arrays2.copyWithout(new int[] {1, 2, 3, 2}, 2));
    }

    @Test
    void copyWithoutShrinksTheArray() {
        assertEquals(2, Arrays2.copyWithout(new int[] {1, 2, 3, 2}, 2).length,
                "the result should be exactly the right size - arrays cannot be resized");
    }

    @Test
    void copyWithoutLeavesTheOriginalAlone() {
        int[] original = {1, 2, 3};
        Arrays2.copyWithout(original, 2);
        assertArrayEquals(new int[] {1, 2, 3}, original);
    }

    @Test
    void copyWithoutRemovingEverything() {
        assertEquals(0, Arrays2.copyWithout(new int[] {5, 5}, 5).length);
    }

    @Test
    void gridHasTheRightShape() {
        int[][] g = Arrays2.grid(2, 3);
        assertEquals(2, g.length, "grid.length is the number of rows");
        assertEquals(3, g[0].length, "grid[0].length is the width of that row");
    }

    @Test
    void gridContents() {
        assertTrue(Arrays.deepEquals(new int[][] {{0, 1, 2}, {3, 4, 5}}, Arrays2.grid(2, 3)));
    }

    @Test
    void gridRowsAreIndependentObjects() {
        int[][] g = Arrays2.grid(2, 2);
        g[0][0] = 99;
        assertEquals(2, g[1][0], "changing one row must not change another");
    }
}
