---
title: Metadata that gives you away
summary: Files carry more than their contents - author names, timestamps, locations - and parsing a PNG's chunks reveals what it leaks.
order: 3
files: [meta.py]
run: python meta.py
hints:
  - "A PNG is an 8-byte signature followed by chunks. Each chunk is: length (4 bytes, big-endian), type (4 bytes), that many data bytes, then a 4-byte CRC."
  - "`parse_chunks`: start at offset 8, and for each chunk read the length, then the type, then skip length+4 bytes (data plus CRC) to the next."
  - "`dimensions`: the IHDR chunk's data starts with width and height as two big-endian 4-byte integers."
  - "`text_metadata`: a tEXt chunk's data is `keyword\x00value`. Collect them into a dict."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **metadata** | data about a file rather than its visible content: author, dates, software, location |
| **EXIF** | the metadata format inside photos from cameras and phones, often with GPS position |
| **GPS coordinates** | a position as latitude and longitude, such as `51.5074,-0.1278` |
| **PNG** | a lossless image format, built from chunks |
| **signature** | the 8 bytes every PNG starts with: `89 50 4e 47 0d 0a 1a 0a` |
| **chunk** | one block of a PNG: length, type, data, CRC |
| **chunk length** | 4 bytes, big-endian: the size of the chunk's **data only** |
| **chunk type** | 4 ASCII letters naming the chunk, such as `IHDR` |
| **CRC** | a 4-byte checksum after the data, used to detect damage |
| **IHDR** | the header chunk; its data starts with width and height |
| **tEXt** | a text metadata chunk: `keyword`, a zero byte, then the value |
| **IDAT** | the compressed picture itself |
| **IEND** | the empty chunk that marks the end of the file |
| **Latin-1** | the simple one-byte text encoding PNG text uses |
| **null byte** (`\x00`) | a byte with value 0, used here as a separator |
| **stripping metadata** | removing it before sharing a file |
| **privacy leak** | sharing more about yourself than you meant to |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `exiftool file` | shows every metadata field a file carries |
| `exiftool -all= file` | removes all metadata (keeps a backup copy named `file_original`) |
| `strings file` | quick look: tEXt values are plain text and show up |
| `python meta.py` | runs your program: prints the sample image's size and metadata |

### Python names

| Name | What it does |
|---|---|
| `from png_data import SAMPLE_PNG` | the lesson's sample image, as bytes |
| `struct.unpack("!I", four_bytes)[0]` | one 4-byte big-endian number |
| `struct.unpack("!II", body[:8])` | two of them: width and height |
| `offset += 8 + length + 4` | skip the chunk's length and type (8), its data, and its CRC (4) |
| `ctype.decode("latin1")` | the type's bytes as a string, `"IHDR"` |
| `body.partition(b"\x00")` | splits at the first null byte into keyword, separator, value |
| `chunks.append((ctype, body))` | adds a `(type, data)` pair to the list |

---

A file is rarely just what you see. Photos, documents and PDFs carry
**metadata**: who made them, when, with what software, and for photos, often
exactly where. People share a file thinking they are sharing a picture, and
hand over their home address with it. For an investigator, metadata is
evidence. For everyone, it is a privacy lesson.

## What files say about themselves

| File | Typical metadata |
|---|---|
| a phone photo (EXIF) | phone model, date and time, **GPS coordinates** |
| a Word document | author's name, company, editing time, earlier authors |
| a PDF | the program that made it, creation and change dates, author |
| a PNG | text chunks with any keyword: author, comment, software |

The usual tool is `exiftool`, which reads (and removes) all of these. In this
lesson you read PNG metadata by hand, because the format is simple and the
skill, walking a structure, carries over to every format.

## How a PNG is built

A PNG is an 8-byte **signature** followed by a sequence of **chunks**. Every
chunk is laid out the same way:

```text
length (4 bytes) | type (4 bytes) | data (length bytes) | CRC (4 bytes)
```

- The **length** is a big-endian 4-byte number and counts **only the data**,
  not the type or the CRC.
- The **type** is four ASCII letters.
- The **CRC** is a checksum for detecting damage; here you just skip it.

The chunk types that matter for this lesson:

| Type | Holds |
|---|---|
| `IHDR` | the header; its data starts with width and height, each a 4-byte big-endian number |
| `tEXt` | text metadata: `keyword`, a **null byte** (`\x00`), then the value |
| `IDAT` | the compressed image |
| `IEND` | nothing: it marks the end |

Here are the chunks of the lesson's sample image:

```pycon
>>> from png_data import SAMPLE_PNG
>>> from meta import parse_chunks
>>> [(ctype, len(body)) for ctype, body in parse_chunks(SAMPLE_PNG)]
[('IHDR', 13), ('tEXt', 15), ('tEXt', 32), ('IDAT', 11), ('IEND', 0)]
```

A tiny picture, two pixels by two, with two text chunks: 47 bytes of
metadata for 11 bytes of picture.

## Walking the chunks

The method is the one you used for pcap files in Network lesson 2:

1. Start at byte 8, just after the signature.
2. Read the 4-byte length and the 4-byte type.
3. Take the next `length` bytes as the data.
4. Skip the 4-byte CRC, and repeat from step 2 until the data runs out.

So each chunk moves you forward `8 + length + 4` bytes.

Do that, look for the `tEXt` chunks, split each at its null byte, and the
file's hidden labelling falls out. The sample turns out to carry an author's
name and a comment with GPS coordinates, which point to central London.

## The takeaway

**Stripping metadata** before publishing is a real defensive habit, and
`exiftool -all= file` does it. Many social networks strip photo GPS data on
upload; email attachments and files shared directly usually keep it. Knowing
how to **read** metadata is how you discover what a file is quietly telling
the world.

## Your turn

`SAMPLE_PNG` is given to you in `png_data.py`. In `meta.py`:

- `parse_chunks(data)`: a list of `(type, data_bytes)` for each chunk, in file
  order, with `type` as a string such as `"IHDR"`.
- `dimensions(data)`: `(width, height)` from the IHDR chunk.
- `text_metadata(data)`: a dict of every tEXt keyword to its value, both as
  strings. PNG text is Latin-1: use `.decode("latin-1")`.

Run it:

```text
size: (2, 2)
metadata: {'Author': 'Jane Doe', 'Comment': 'taken at 51.5074,-0.1278'}
```

## Check yourself

1. What is metadata?
   *Data about a file: author, dates, software, location.*
2. What does a PNG chunk's length count?
   *Only the data: not the type or the CRC.*
3. How far forward is the next chunk?
   *8 + length + 4 bytes from the start of this one.*
4. How is a tEXt chunk's data laid out?
   *Keyword, a null byte, then the value.*
5. Why strip metadata before publishing a photo?
   *It may reveal where you were, or who you are.*
