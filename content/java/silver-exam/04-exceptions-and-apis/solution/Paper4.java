import java.time.Month;
import java.time.Year;

public class Paper4 {

    @SuppressWarnings("finally")
    public static int finallyWins() {
        try {
            return 1;
        } finally {
            return 2;
        }
    }

    public static String classify(Runnable action) {
        try {
            action.run();
            return "none";
        } catch (RuntimeException e) {
            return e.getClass().getSimpleName();
        }
    }

    public static Integer sumOrNull(Integer a, Integer b) {
        if (a == null || b == null) {
            return null;
        }
        return a + b;
    }

    public static boolean isLeap(int year) {
        return Year.isLeap(year);
    }

    public static String monthName(int month) {
        return Month.of(month).name();
    }

    public static void main(String[] args) {
        System.out.println(finallyWins() + " " + monthName(1));
    }
}
