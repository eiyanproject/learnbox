public class Safe {

    public static int parseOrDefault(String s, int fallback) {
        try {
            return Integer.parseInt(s);
        } catch (NumberFormatException e) {
            return fallback;
        }
    }

    public static int divide(int a, int b) {
        if (b == 0) {
            throw new ArithmeticException("/ by zero");
        }
        return a / b;
    }

    public static String describe(Runnable action) {
        try {
            action.run();
            return "ok";
        } catch (IllegalArgumentException e) {
            return "bad argument";
        } catch (RuntimeException e) {
            return "failed";
        }
    }

    public static String closeOrder() {
        StringBuilder log = new StringBuilder();
        class Res implements AutoCloseable {
            private final String name;

            Res(String name) {
                this.name = name;
            }

            @Override
            public void close() {
                if (log.length() > 0) {
                    log.append(',');
                }
                log.append(name);
            }
        }
        try (Res a = new Res("A"); Res b = new Res("B")) {
            // nothing to do; the point is the closing order
        }
        return log.toString();
    }

    public static void main(String[] args) {
        System.out.println(parseOrDefault("12", 0) + " " + closeOrder());
    }
}
