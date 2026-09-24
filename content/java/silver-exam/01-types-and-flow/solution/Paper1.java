public class Paper1 {

    public static int evaluate(int a, int b) {
        return a / b;
    }

    public static String promote(String leftType, String rightType) {
        if (leftType.equals("double") || rightType.equals("double")) {
            return "double";
        }
        if (leftType.equals("float") || rightType.equals("float")) {
            return "float";
        }
        if (leftType.equals("long") || rightType.equals("long")) {
            return "long";
        }
        return "int";
    }

    public static String ternaryChain(int n) {
        return n < 0 ? "negative" : n == 0 ? "zero" : "positive";
    }

    public static String fizzOrBuzz(int n) {
        if (n % 15 == 0) {
            return "FizzBuzz";
        }
        if (n % 3 == 0) {
            return "Fizz";
        }
        if (n % 5 == 0) {
            return "Buzz";
        }
        return String.valueOf(n);
    }

    public static byte compound(byte start, int add) {
        byte b = start;
        b += add;
        return b;
    }

    public static void main(String[] args) {
        System.out.println(evaluate(7, 2) + " " + compound((byte) 10, 300));
    }
}
