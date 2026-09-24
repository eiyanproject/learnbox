import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.Collectors;

public class Tool {

    record Options(String command, String file, String pattern, boolean verbose) {}

    static String usage() {
        return "Usage: tool <count|words|find> --file <path> [--pattern <text>] [--verbose]";
    }

    static Options parse(String[] args) {
        String command = null;
        String file = null;
        String pattern = null;
        boolean verbose = false;

        for (int i = 0; i < args.length; i++) {
            String arg = args[i];
            switch (arg) {
                case "--file" -> {
                    if (++i >= args.length) {
                        throw new IllegalArgumentException("--file needs a value");
                    }
                    file = args[i];
                }
                case "--pattern" -> {
                    if (++i >= args.length) {
                        throw new IllegalArgumentException("--pattern needs a value");
                    }
                    pattern = args[i];
                }
                case "--verbose" -> verbose = true;
                default -> {
                    if (arg.startsWith("-")) {
                        throw new IllegalArgumentException("Unknown option: " + arg);
                    }
                    if (command != null) {
                        throw new IllegalArgumentException("Unexpected argument: " + arg);
                    }
                    command = arg;
                }
            }
        }
        if (command == null) {
            throw new IllegalArgumentException("No command given");
        }
        return new Options(command, file, pattern, verbose);
    }

    static String run(Options options, List<String> lines) {
        return switch (options.command()) {
            case "count" -> String.valueOf(lines.size());
            case "words" -> String.valueOf(lines.stream()
                    .flatMap(l -> java.util.Arrays.stream(l.trim().split("\\s+")))
                    .filter(w -> !w.isEmpty())
                    .count());
            case "find" -> {
                if (options.pattern() == null) {
                    throw new IllegalArgumentException("find needs --pattern");
                }
                yield lines.stream()
                        .filter(l -> l.contains(options.pattern()))
                        .collect(Collectors.joining(System.lineSeparator()));
            }
            default -> throw new IllegalArgumentException("Unknown command: " + options.command());
        };
    }

    public static void main(String[] args) {
        try {
            Options options = parse(args);
            List<String> lines = options.file() == null
                    ? List.of()
                    : Files.readAllLines(Path.of(options.file()));
            System.out.println(run(options, lines));
        } catch (IllegalArgumentException e) {
            System.err.println(e.getMessage());
            System.err.println(usage());
            System.exit(2);
        } catch (IOException e) {
            System.err.println("Cannot read the file: " + e.getMessage());
            System.exit(1);
        }
    }
}
