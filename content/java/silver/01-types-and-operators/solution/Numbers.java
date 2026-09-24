public class Numbers {

    public static double averageOf(int a, int b) {
        return (a + b) / 2.0;
    }

    public static int narrow(long value) {
        return (int) value;
    }

    public static int overflowed() {
        return Integer.MAX_VALUE + 1;
    }

    public static boolean isEven(int n) {
        return n % 2 == 0;
    }

    public static char nextLetter(char c) {
        return (char) (c + 1);
    }

    public static void main(String[] args) {
        System.out.println(averageOf(7, 2));
        System.out.println(overflowed());
    }
}
