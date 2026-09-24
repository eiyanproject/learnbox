import java.util.Arrays;

public class Paper2 {

    public static String chained(String s) {
        return s.trim().replace(" ", "_").toUpperCase();
    }

    public static boolean identical(String a, String b) {
        return a == b;
    }

    public static boolean equivalent(String a, String b) {
        return a.equals(b);
    }

    public static boolean sameElements(int[] a, int[] b) {
        return Arrays.equals(a, b);
    }

    public static String describe(int[] values) {
        return Arrays.toString(values) + " len=" + values.length;
    }

    public static String middle(String s) {
        int third = s.length() / 3;
        return s.substring(third, third * 2);
    }

    public static void main(String[] args) {
        System.out.println(chained("  hello world "));
        System.out.println(describe(new int[] {1, 2, 3}));
    }
}
