from forensics_data import CARVE_BLOB

PNG_SIG = b"\x89PNG\r\n\x1a\n"


def carve_png(blob):
    # Header to footer: locate the signature, then the IEND that closes it, and
    # return everything between - the file, lifted out of the surrounding junk.
    start = blob.find(PNG_SIG)
    if start == -1:
        return None
    iend = blob.find(b"IEND", start)
    if iend == -1:
        return None
    end = iend + 4 + 4   # IEND type plus its CRC
    return blob[start:end]


if __name__ == "__main__":
    png = carve_png(CARVE_BLOB)
    print("carved" if png else "nothing", len(png) if png else 0, "bytes")
