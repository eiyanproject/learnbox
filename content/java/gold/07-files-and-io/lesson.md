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

The modern API is `java.nio.file`: `Path` for locations and `Files` for
operations. The old `java.io.File` is still everywhere in existing code, and
the exam expects you to know both exist and prefer the new one.

```java
Path p = Path.of("data", "notes.txt");     // portable joining, no separators
Files.writeString(p, "hello");
String text = Files.readString(p);
```

`Path` is just a location — creating one touches no disk and a path to a
nonexistent file is perfectly legal. `Files` is where anything actually
happens.

## Reading

| | |
|---|---|
| `Files.readString(p)` | the whole file as one String |
| `Files.readAllLines(p)` | a `List<String>`, all in memory |
| `Files.lines(p)` | a lazy `Stream<String>` |
| `Files.newBufferedReader(p)` | a reader for manual control |

The distinction matters: `readAllLines` on a 4 GB log runs out of memory,
`lines` does not. **`Files.lines` returns a stream backed by an open file**, so
it must be closed:

```java
try (Stream<String> lines = Files.lines(path)) {
    return lines.count();
}
```

Forgetting that leaks a file handle for every call — an exam favourite because
it looks like ordinary stream code.

## Writing

```java
Files.writeString(p, text);                                  // truncates
Files.writeString(p, text, StandardOpenOption.APPEND);       // appends
Files.createDirectories(p.getParent());                      // mkdir -p
```

## Useful checks

`Files.exists`, `Files.isDirectory`, `Files.size`, `Files.delete` (throws if
missing) against `Files.deleteIfExists` (does not).

Most of these throw `IOException`, which is **checked** — so every method
touching files either handles it or declares `throws IOException`. That is not
an accident; the filesystem is exactly the kind of failure the checked
mechanism was designed for.

## Your turn

In `Files2.java`:

- `public static void save(Path path, String text)` — creating parent
  directories as needed
- `public static String load(Path path, String fallback)` — the fallback when
  the file does not exist
- `public static long countLines(Path path)` — streamed, with the stream closed
- `public static void append(Path path, String line)`
- `public static List<String> findContaining(Path path, String needle)`
