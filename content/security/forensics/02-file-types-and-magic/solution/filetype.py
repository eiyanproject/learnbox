MAGICS = [
    (b"\x89PNG\r\n\x1a\n", "png"),
    (b"%PDF", "pdf"),
    (b"\x7fELF", "elf"),
    (b"PK\x03\x04", "zip"),
    (b"\xff\xd8\xff", "jpeg"),
    (b"\x1f\x8b", "gzip"),
]

EXT_TYPES = {"png": "png", "pdf": "pdf", "zip": "zip",
             "jpg": "jpeg", "jpeg": "jpeg", "gz": "gzip"}


def identify(data):
    # The type is whichever signature the bytes begin with.
    for sig, name in MAGICS:
        if data.startswith(sig):
            return name
    return "unknown"


def extension_mismatch(filename, data):
    # Trust the bytes, not the label. A recognised type that contradicts the
    # claimed extension is the disguised-file red flag.
    real = identify(data)
    if real == "unknown":
        return False
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    claimed = EXT_TYPES.get(ext)
    return claimed is not None and claimed != real


if __name__ == "__main__":
    print(identify(b"\x7fELF\x02\x01"))
    print("disguised?", extension_mismatch("invoice.jpg", b"\x7fELF..."))
