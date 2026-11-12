---
title: Files, paths and NIO.2
summary: Path against File, reading a whole file against streaming it, and the try-with-resources that closes what you open.
order: 7
files: [Files2.java]
run: javac Files2.java && java Files2
hints:
  - "`Files.writeString(path, text)` and `Files.readString(path)` are the one-line forms for small files."
  - "`countLines` should stream rather than load everything: `try (Stream<String> lines = Files.lines(path)) { return lines.count(); }` - and that stream MUST be closed, which is why it needs try-with-resources."
  - "`Files.exists(path)` before reading, or catch NoSuchFileException - the test checks the missing-file case returns the fallback."
  - "`Path.of(\"a\", \"b\")` joins segments portably; do not concatenate with \"/\"."
---

Programs read configuration, write logs, and load and save data, and all of
that is files. Java has had two file APIs. The old `java.io.File` is still
everywhere in existing code; the modern one, **NIO.2** (Java 7, in
`java.nio.file`), splits the job in two: `Path` for locations and `Files` for
operations. The exam expects you to know both exist and prefer the new one,
which has clearer errors and far more convenient methods.

```java
Path p = Path.of("data", "notes.txt");     // portable joining, no separators
Files.writeString(p, "hello");
String text = Files.readString(p);
```

(A fragment.) `Path.of("data", "notes.txt")` builds the path
`data/notes.txt`, putting in the right separator for the operating system
(`/` on Linux and macOS, `\` on Windows) so you never write one by hand. A
path without a leading `/` is **relative**: it is resolved against the
current directory, the one the program was started from.

You will still meet `java.io.File`, `FileReader` and `BufferedReader` all
over older code and in search results. They work, but for new code they are
obsolete: `Files` does the same jobs in fewer lines, with clearer exceptions
(a missing file is a `NoSuchFileException` that names it, rather than a
general `FileNotFoundException` or just `false`).

Text in a file is stored as bytes, and an **encoding** says how characters
map to bytes. Since Java 18 the default is UTF-8 everywhere, so `readString`
and `writeString` need no encoding argument; before that the default
depended on the operating system, and older code passes
`StandardCharsets.UTF_8` explicitly for that reason.

`Path` is just a location — creating one touches no disk and a path to a
nonexistent file is perfectly legal. `Files` is where anything actually
happens: every method on it is static and takes a `Path`.
`dir.resolve("notes.txt")` gives the path of `notes.txt` inside `dir`, and
`p.getParent()` gives the folder containing `p`.

## Reading

| | |
|---|---|
| `Files.readString(p)` | the whole file as one String |
| `Files.readAllLines(p)` | a `List<String>`, all in memory |
| `Files.lines(p)` | a lazy `Stream<String>` |
| `Files.newBufferedReader(p)` | a reader for manual control |

The distinction matters: `readAllLines` on a 4 GB log runs out of memory,
`lines` does not, because it reads one line at a time as the stream asks for
them (the same laziness as any stream). **`Files.lines` returns a stream
backed by an open file**, so it must be closed:

```java
try (Stream<String> lines = Files.lines(path)) {
    return lines.count();
}
```

(A fragment from inside a method.) A stream is `AutoCloseable`, so
try-with-resources closes it, and with it the file, when the block ends, even
if counting throws.

Forgetting that leaks a **file handle** for every call — an exam favourite
because it looks like ordinary stream code. A file handle is the operating
system's record of an open file; each process may only have a limited number
open, and a file held open may not be deletable (on Windows in particular).
Streams from collections hold nothing and need no closing; only streams over
an I/O resource do.

## Writing

```java
Files.writeString(p, text);                                  // truncates
Files.writeString(p, text, StandardOpenOption.APPEND);       // appends
Files.createDirectories(p.getParent());                      // mkdir -p
```

**Truncate** means empty the file first: the plain form creates the file if
needed and replaces whatever it held. `APPEND` adds to the end instead, but
fails if the file does not exist yet, unless you also pass
`StandardOpenOption.CREATE`. Writing into a folder that does not exist fails
with `NoSuchFileException`; `createDirectories` creates every missing folder
along the path (like the shell's `mkdir -p`) and does nothing if they already
exist.

## Useful checks

`Files.exists`, `Files.isDirectory`, `Files.size`, `Files.delete` (throws if
missing) against `Files.deleteIfExists` (does not).

Most of these throw `IOException`, which is **checked** — so every method
touching files either handles it or declares `throws IOException`. That is not
an accident; the filesystem is exactly the kind of failure the checked
mechanism was designed for. `NoSuchFileException`, thrown for a missing file,
is a subclass of `IOException`.

There is a third option, common when a method's signature must not declare
`throws` (for example when it is used inside a lambda, or a caller cannot
sensibly recover): catch the checked exception and rethrow it wrapped in the
unchecked `UncheckedIOException`, keeping the original as its cause:

```java
public static String readOrFail(Path p) {
    try {
        return Files.readString(p);
    } catch (IOException e) {
        throw new UncheckedIOException(e);
    }
}
```

The error still stops the program if nobody handles it, and the original
`IOException`, with its message, is available from `getCause()`.

## Run

```java
import java.io.IOException;
import java.nio.file.*;
import java.util.stream.Stream;

public class FilesDemo {
    public static void main(String[] args) throws IOException {
        Path ghost = Path.of("no", "such", "file.txt");      // touches no disk
        System.out.println(ghost + " exists? " + Files.exists(ghost));

        Path dir = Files.createTempDirectory("lesson");
        Path p = dir.resolve("notes.txt");
        Files.writeString(p, "one\ntwo\n");
        Files.writeString(p, "three\n", StandardOpenOption.APPEND);
        try (Stream<String> lines = Files.lines(p)) {
            System.out.println(lines.count() + " lines");
        }
        System.out.println(Files.readAllLines(p));

        Files.delete(p);
        System.out.println(Files.deleteIfExists(p));
        try {
            Files.delete(p);
        } catch (NoSuchFileException e) {
            System.out.println("delete: NoSuchFileException");
        }
        Files.delete(dir);
    }
}
```

```output
no/such/file.txt exists? false
3 lines
[one, two, three]
false
delete: NoSuchFileException
```

The path to a file that does not exist was created without error, and
`exists` simply said `false`. `createTempDirectory` made a fresh folder for
the demo. The second `writeString`, with `APPEND`, added a third line rather
than replacing the first two. After `Files.delete`, `deleteIfExists` found
nothing to delete and returned `false`, while a second `delete` threw. `main`
declares `throws IOException` so the example need not handle each call.

## Your turn

In `Files2.java`:

None of these methods declares `throws IOException`: the tests call them
without handling one, so a `throws` clause would stop the tests from
compiling. Catch `IOException` inside each method and rethrow it as an
`UncheckedIOException`, as shown above.

- `public static void save(Path path, String text)` — write `text` to the
  file, replacing what was there, creating parent directories as needed
- `public static String load(Path path, String fallback)` — the file's whole
  contents, or `fallback` when the file does not exist
- `public static long countLines(Path path)` — the number of lines, streamed
  with `Files.lines` and with the stream closed (a test deletes the file
  straight afterwards); an empty file has 0
- `public static void append(Path path, String line)` — add `line` as a new
  line at the end of the file (so add the `"\n"` yourself), creating the file
  if it does not exist yet: two appends make a file of two lines
- `public static List<String> findContaining(Path path, String needle)` — the
  lines that contain `needle`, in order; an empty list if none do
