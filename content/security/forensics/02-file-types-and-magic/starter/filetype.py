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
    pass


def extension_mismatch(filename, data):
    pass


if __name__ == "__main__":
    print(identify(b"\x7fELF\x02\x01"))
    print("disguised?", extension_mismatch("invoice.jpg", b"\x7fELF..."))
