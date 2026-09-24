public class Text {

    public static String shout(String s) {
        return s.trim().toUpperCase() + "!";
    }

    public static String reverse(String s) {
        return new StringBuilder(s).reverse().toString();
    }

    public static boolean sameContent(String a, String b) {
        return a.equals(b);
    }

    public static String initials(String fullName) {
        StringBuilder out = new StringBuilder();
        for (String part : fullName.trim().split("\\s+")) {
            if (!part.isEmpty()) {
                out.append(Character.toUpperCase(part.charAt(0))).append('.');
            }
        }
        return out.toString();
    }

    public static void main(String[] args) {
        System.out.println(shout("  hello "));
        System.out.println(initials("ada lovelace"));
    }
}
