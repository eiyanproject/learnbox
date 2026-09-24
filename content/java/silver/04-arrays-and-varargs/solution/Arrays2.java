public class Arrays2 {

    public static int sum(int... values) {
        int total = 0;
        for (int v : values) {
            total += v;
        }
        return total;
    }

    public static int largest(int[] values) {
        if (values.length == 0) {
            throw new IllegalArgumentException("no largest element of an empty array");
        }
        int best = values[0];
        for (int v : values) {
            if (v > best) {
                best = v;
            }
        }
        return best;
    }

    public static int[] copyWithout(int[] values, int unwanted) {
        int keep = 0;
        for (int v : values) {
            if (v != unwanted) {
                keep++;
            }
        }
        int[] out = new int[keep];
        int i = 0;
        for (int v : values) {
            if (v != unwanted) {
                out[i++] = v;
            }
        }
        return out;
    }

    public static int[][] grid(int rows, int cols) {
        int[][] out = new int[rows][cols];
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                out[r][c] = r * cols + c;
            }
        }
        return out;
    }

    public static void main(String[] args) {
        System.out.println(sum(1, 2, 3));
    }
}
