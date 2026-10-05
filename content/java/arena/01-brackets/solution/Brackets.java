import java.util.ArrayDeque;
import java.util.Deque;

public class Brackets {

    private static final String OPEN = "([{";
    private static final String CLOSE = ")]}";

    public static boolean balanced(String s) {
        return depth(s) >= 0;
    }

    public static int depth(String s) {
        Deque<Character> stack = new ArrayDeque<>();
        int deepest = 0;
        for (char c : s.toCharArray()) {
            if (OPEN.indexOf(c) >= 0) {
                stack.push(c);
                deepest = Math.max(deepest, stack.size());
            } else if (CLOSE.indexOf(c) >= 0) {
                if (stack.isEmpty() || OPEN.indexOf(stack.pop()) != CLOSE.indexOf(c)) {
                    return -1;
                }
            }
        }
        return stack.isEmpty() ? deepest : -1;
    }

    public static void main(String[] args) {
        System.out.println(balanced("(a[0] + {b})"));
    }
}
