public class Roman {

    private static final int[] VALUES = {1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1};
    private static final String[] SYMBOLS = {"M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"};

    public static String toRoman(int n) {
        if (n < 1 || n > 3999) {
            throw new IllegalArgumentException("out of range: " + n);
        }
        StringBuilder out = new StringBuilder();
        for (int i = 0; i < VALUES.length; i++) {
            while (n >= VALUES[i]) {
                out.append(SYMBOLS[i]);
                n -= VALUES[i];
            }
        }
        return out.toString();
    }

    public static int fromRoman(String s) {
        int total = 0;
        int at = 0;
        for (int i = 0; i < VALUES.length; i++) {
            while (s.startsWith(SYMBOLS[i], at)) {
                total += VALUES[i];
                at += SYMBOLS[i].length();
            }
        }
        return total;
    }

    public static void main(String[] args) {
        System.out.println(toRoman(1994));
    }
}
