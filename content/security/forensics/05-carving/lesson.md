---
title: Carving a file out of a blob
summary: Recovering a file from raw bytes - a disk image, a memory dump - by finding where it starts and where it ends.
order: 5
files: [carve.py]
run: python carve.py
hints:
  - "A PNG starts with the 8-byte signature and ends at the IEND chunk plus its 4-byte CRC."
  - "`carve_png`: find the signature with `.find`, find `IEND` after it, and return from the signature to 8 bytes past the start of IEND (the `IEND` type is 4 bytes, its CRC another 4)."
  - "Return `None` when there is no complete PNG - no signature, or no IEND after it."
  - "This is file carving: recovering a file by its structure alone, with no filesystem to tell you where it is."
---

When a file is deleted, its directory entry goes but its bytes often remain on
disk until overwritten. **File carving** recovers them with no filesystem to
help - by scanning raw bytes for the **start and end signatures** of a known
format and cutting out everything between. It is how deleted photos are
recovered from a memory card and how embedded files are pulled from a dump.

## Start and end

A format you can carve has a recognisable header and a recognisable end:

- A PNG **starts** at its 8-byte signature.
- It **ends** at the IEND chunk - the type `IEND` plus its 4-byte CRC.

Find the signature in the blob, find the IEND after it, and the bytes from one
to the other are the file - surrounded by whatever junk shares the medium. The
same approach carves JPEGs (`FF D8` to `FF D9`), PDFs, and more; each is a
header-to-footer scan.

## Your turn

`CARVE_BLOB` - a PNG buried in junk - is provided in `forensics_data.py`. In
`carve.py`:

- `carve_png(blob)` - the exact bytes of the PNG embedded in the blob: from the
  first byte of its signature through the 4-byte CRC that follows `IEND`. Return
  `None` if there is no complete PNG (no signature, or no `IEND` after it)
