public class Flow {

    public static String grade(int score) {
        if (score >= 90) return "A";
        if (score >= 80) return "B";
        if (score >= 70) return "C";
        if (score >= 60) return "D";
        return "F";
    }

    public static String dayType(int day) {
        return switch (day) {
            case 1, 2, 3, 4, 5 -> "weekday";
            case 6, 7 -> "weekend";
            default -> "invalid";
        };
    }

    public static int firstMultiple(int[] values, int n) {
        for (int v : values) {
            if (v % n == 0) {
                return v;
            }
        }
        return -1;
    }

    public static String countdown(int from) {
        StringBuilder out = new StringBuilder();
        for (int i = from; i >= 1; i--) {
            if (out.length() > 0) {
                out.append(',');
            }
            out.append(i);
        }
        return out.toString();
    }

    public static void main(String[] args) {
        System.out.println(grade(85) + " " + dayType(6) + " " + countdown(3));
    }
}
