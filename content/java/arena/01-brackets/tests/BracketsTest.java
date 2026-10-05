import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

class BracketsTest {

    @Test
    void balancedCode() {
        assertTrue(Brackets.balanced("(a[0] + {b})"));
        assertTrue(Brackets.balanced("()[]{}"));
        assertTrue(Brackets.balanced("{[()()]}"));
    }

    @Test
    void nothingToBalance() {
        assertTrue(Brackets.balanced(""));
        assertTrue(Brackets.balanced("no brackets here"));
    }

    @Test
    void wrongKind() {
        assertFalse(Brackets.balanced("(]"));
        assertFalse(Brackets.balanced("{)"));
    }

    @Test
    void wrongOrder() {
        assertFalse(Brackets.balanced("([)]"));
    }

    @Test
    void neverClosed() {
        assertFalse(Brackets.balanced("(("));
        assertFalse(Brackets.balanced("f(a[i]"));
    }

    @Test
    void closedBeforeOpened() {
        assertFalse(Brackets.balanced(")("));
        assertFalse(Brackets.balanced("]"));
        assertFalse(Brackets.balanced("a) + (b"));
    }

    @Test
    void depthOfFlatText() {
        assertEquals(0, Brackets.depth(""));
        assertEquals(0, Brackets.depth("abc"));
    }

    @Test
    void depthCountsNestingNotPairs() {
        assertEquals(1, Brackets.depth("()[]"));
        assertEquals(2, Brackets.depth("f(a[i], {x})"));
        assertEquals(4, Brackets.depth("{[(())]}()"));
    }

    @Test
    void depthOfUnbalancedIsMinusOne() {
        assertEquals(-1, Brackets.depth("(]"));
        assertEquals(-1, Brackets.depth("(("));
        assertEquals(-1, Brackets.depth(")("));
        assertEquals(-1, Brackets.depth("((()))]"));
    }

    @Test
    void aLongLine() {
        String open = "(".repeat(5000);
        String close = ")".repeat(5000);
        assertTrue(Brackets.balanced(open + close));
        assertEquals(5000, Brackets.depth(open + close));
        assertFalse(Brackets.balanced(open + close + ")"));
    }
}
