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

**Steganography** hides data inside something that looks ordinary. Unlike
encryption, which makes it obvious that *something* is protected, stego aims for
nobody to look at all. Two classic techniques, both findable once you know where
to look.

## Data after the end

A PNG officially ends at its **IEND** chunk. Image viewers stop reading there -
so anything appended after IEND is invisible to them but sits plainly in the
file. It is the simplest hiding place there is, and the simplest to detect: the
file is longer than its own structure says it should be. Carving off that
trailing data is the find.

## Least-significant-bit stego

A pixel's colour value can change by one without any human noticing. **LSB
steganography** hides a message in the lowest bit of each byte: flip those bits
to spell out the secret, and the image looks identical. To read it, collect the
low bit of each byte, pack them back into characters, and a hidden message
appears out of what looked like ordinary pixel data.

The scheme in this lesson packs eight low bits into one character, **most
significant bit first**, and ends the message with a zero byte (eight zero
bits) - read `embed_lsb` to see it done the other way round.

Detecting LSB stego in the wild is harder (it needs statistics), but
**extracting** a known-scheme message is exactly this: the attacker's channel,
and the investigator's recovery, are the same operation.

## Your turn

`embed_lsb(pixels, message)` is provided. In `hidden.py`:

- `data_after_iend(png)` - the bytes hidden after the PNG's IEND chunk, or `b""`
- `extract_lsb(pixels)` - the message hidden in the least-significant bits of
  the pixel bytes, as a string, up to (not including) the zero-byte terminator
