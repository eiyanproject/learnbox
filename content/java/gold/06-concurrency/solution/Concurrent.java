import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Callable;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.atomic.AtomicInteger;

public class Concurrent {

    private static int shared;

    public static int racyCount(int threads, int perThread) {
        shared = 0;
        List<Thread> workers = new ArrayList<>();
        for (int t = 0; t < threads; t++) {
            Thread thread = new Thread(() -> {
                for (int i = 0; i < perThread; i++) {
                    shared++; // deliberately unsynchronised
                }
            });
            workers.add(thread);
            thread.start();
        }
        for (Thread thread : workers) {
            try {
                thread.join();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
        return shared;
    }

    public static int safeCount(int threads, int perThread) {
        AtomicInteger count = new AtomicInteger();
        List<Thread> workers = new ArrayList<>();
        for (int t = 0; t < threads; t++) {
            Thread thread = new Thread(() -> {
                for (int i = 0; i < perThread; i++) {
                    count.incrementAndGet();
                }
            });
            workers.add(thread);
            thread.start();
        }
        for (Thread thread : workers) {
            try {
                thread.join();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
        return count.get();
    }

    public static List<Integer> runAll(List<Callable<Integer>> tasks) throws Exception {
        ExecutorService pool = Executors.newFixedThreadPool(4);
        try {
            List<Integer> out = new ArrayList<>();
            for (Future<Integer> f : pool.invokeAll(tasks)) {
                out.add(f.get());
            }
            return out;
        } finally {
            pool.shutdown();
        }
    }

    public static Map<String, Integer> concurrentTally(List<String> words) {
        Map<String, Integer> counts = new ConcurrentHashMap<>();
        words.parallelStream().forEach(w -> counts.merge(w, 1, Integer::sum));
        return counts;
    }

    public static void main(String[] args) throws Exception {
        System.out.println(safeCount(4, 10000));
    }
}
