---
title: Hidden data
summary: Data smuggled where no one looks - after a file's official end, and in the lowest bit of every pixel.
order: 4
files: [hidden.py]
run: python hidden.py
hints:
  - "`data_after_iend`: find the IEND chunk, which is `\\x00\\x00\\x00\\x00IEND` plus a 4-byte CRC, and return whatever bytes come after it."
  - "The IEND marker in the stream is `b'IEND'`; the chunk ends 4 bytes (the CRC) after the data, and the PNG should end there - anything beyond is hidden."
  - "`extract_lsb`: read the least-significant bit of each byte, gather them 8 at a time into characters (most-significant bit first), and stop at a 0 byte."
  - "`embed_lsb` is provided so you can see how the message got in; your job is to pull it back out."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **steganography** (stego) | hiding data inside something ordinary, so nobody thinks to look |
| **encryption** | hiding what data says; it is obvious that something is protected |
| **carrier** (cover) | the ordinary file the data is hidden in |
| **IEND** | the chunk that officially ends a PNG (Forensics lesson 3) |
| **trailing data** | bytes after a file's official end; viewers ignore them |
| **pixel** | one dot of an image; each colour in it is a byte from 0 to 255 |
| **bit** | one binary digit; a byte is eight of them |
| **least significant bit** (LSB) | the lowest bit of a byte, worth 1; changing it moves the value by at most one |
| **most significant bit first** | the order the bits of each character are stored in: the bit worth 128 comes first |
| **LSB steganography** | hiding a message in the lowest bit of each byte of an image |
| **terminator** | a marker for the end of the message; here a zero byte (eight zero bits) |
| **detect** vs **extract** | noticing that something is hidden, versus reading it out once you know the scheme |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `xxd file \| tail` | shows the last bytes of a file, where appended data sits |
| `strings file` | prints readable text, including text appended after IEND |
| `python hidden.py` | runs your program: hides a message in some bytes and reads it back |

### Python names

| Name | What it does |
|---|---|
| `png.find(b"IEND")` | the position of `IEND` in the bytes, or `-1` if absent |
| `marker + 4 + 4` | past the four letters `IEND` and the 4-byte CRC |
| `png[end:]` | everything from that position to the end |
| `byte & 1` | the lowest bit of a byte: 0 or 1 |
| `(value << 1) \| bit` | shifts the bits collected so far left and adds the new one at the bottom |
| `chr(value)` | the character for that number |
| `break` | stops the loop: the terminator was found |
| `embed_lsb(pixels, message)` | given to you: hides `message` and a zero byte in the low bits |
| `out[i] & 0xFE` | the byte with its lowest bit cleared (`0xFE` is `11111110`) |
| `bytearray(pixels)` | a changeable copy of the bytes |
| `CLEAN_PNG`, `STEGO_PNG` | sample images in `forensics_data.py`, without and with appended data |

---

**Steganography** hides data inside something that looks ordinary. It is
the opposite of encryption in one way: encryption makes it obvious that
**something** is protected, while steganography tries to make sure nobody
looks at all. This lesson covers two classic techniques, both easy to find
once you know where to look.

The Trail of Bits guide notes that steganography is rare in real
investigations and common in CTF puzzles. But both techniques here teach
something general: a file can hold more than its format admits.

## Hiding place 1: after the end

A PNG officially ends at its **IEND** chunk (Forensics lesson 3). Image
viewers stop reading there. Anything appended after IEND is invisible to
them, yet it sits plainly in the file.

```pycon
>>> from forensics_data import CLEAN_PNG, STEGO_PNG
>>> len(CLEAN_PNG), len(STEGO_PNG)      # the same picture, two sizes
(69, 103)
>>> STEGO_PNG[-34:]
b'SECRET: the meeting is at midnight'
```

Both open as the same two-by-two image, but one is 34 bytes longer. This is
the simplest hiding place there is, and the simplest to detect: the file is
longer than its own structure says it should be. To recover the data:

1. find `IEND`;
2. skip its four letters and the 4-byte CRC after them;
3. everything left is **trailing data**.

`strings` or `xxd file | tail` would also show it here, because the hidden
text is readable.

## Hiding place 2: the lowest bit of every byte

Each colour of each **pixel** is a byte from 0 to 255. Change a byte by one,
say from 102 to 103, and no human can see the difference. The bit that makes
that difference is the **least significant bit** (LSB).

**LSB steganography** hides a message in those bits:

1. Turn the message into bits: each character is 8 bits, **most significant
   bit first**. `A` is 65, which is `01000001`.
2. Put one message bit into the lowest bit of each pixel byte, one byte per
   bit.
3. End with a zero byte, eight zero bits, as a **terminator**.

```pycon
>>> from hidden import embed_lsb
>>> list(embed_lsb(bytes(range(100, 116)) * 2, "A")[:8])
[100, 101, 102, 102, 104, 104, 106, 107]
```

The first eight bytes were 100 to 107. Their lowest bits now spell
`0 1 0 0 0 0 0 1`: an `A`. Each byte moved by one at most, so the picture
looks the same.

To read it back, reverse the steps: take the lowest bit of each byte
(`byte & 1`), collect them eight at a time, build each character with
`value = (value << 1) | bit`, and stop at the zero byte.

**Detecting** LSB hiding in an unknown image is hard: it needs statistics,
because the changed bits look like natural noise. **Extracting** a message
once you know the scheme is simply this. The hider's channel and the
investigator's recovery are the same operation, run in opposite directions.

## Your turn

`embed_lsb(pixels, message)` is given to you, so you can see how a message
gets in. In `hidden.py`:

- `data_after_iend(png)`: the bytes hidden after the PNG's IEND chunk (and its
  CRC), or `b""` if there are none or there is no IEND.
- `extract_lsb(pixels)`: the message hidden in the lowest bits of the bytes,
  as a string, up to but not including the zero-byte terminator.

Run it:

```text
recovered: hi there
```

## Check yourself

1. How does steganography differ from encryption?
   *It hides that there is a message at all; encryption hides only what it
   says.*
2. Why can't an image viewer see data after IEND?
   *It stops reading at the official end of the file.*
3. What gives away appended data?
   *The file is longer than its chunks say it should be.*
4. What is the lowest bit of 107?
   *1: 107 is odd.*
5. How does `extract_lsb` know where the message ends?
   *It stops at a zero byte, eight zero bits.*
