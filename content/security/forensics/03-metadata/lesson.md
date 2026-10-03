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

A file is rarely just its visible contents. Photos, documents and PDFs carry
**metadata**: who created them, when, with what software, and - notoriously for
photos - exactly where. People share a file believing they are sharing a
picture, and hand over their home address in the process. For an investigator
this is evidence; for everyone it is a privacy lesson.

## PNG structure

A PNG is an 8-byte signature then a sequence of **chunks**, each laid out the
same way:

```text
length (4 bytes) | type (4 bytes) | data (length bytes) | CRC (4 bytes)
```

The length is a big-endian 4-byte integer and counts only the data, not the
type or CRC; the type is four ASCII letters.

- **IHDR** - the header; its data begins with width and height, each a
  big-endian 4-byte integer.
- **tEXt** - optional text metadata, stored as `keyword\x00value`. This is
  where an author name or a comment with GPS coordinates hides.
- **IEND** - marks the end.

Walking the chunks is the same discipline as the pcap: read a length, take that
many bytes, move on. Do it and the file's hidden labelling falls out.

## The takeaway

Stripping metadata before publishing is a real defensive habit - `exiftool`
exists largely for this. Knowing how to *read* it is how you discover what a
file is quietly telling the world.

## Your turn

`SAMPLE_PNG` is provided in `png_data.py`. In `meta.py`:

- `parse_chunks(data)` - a list of `(type, data_bytes)` for each chunk, in file
  order, with `type` as a string such as `"IHDR"`
- `dimensions(data)` - `(width, height)` from the IHDR chunk
- `text_metadata(data)` - a dict of every tEXt keyword to its value, both as
  strings (PNG text is Latin-1: `.decode("latin-1")`)
