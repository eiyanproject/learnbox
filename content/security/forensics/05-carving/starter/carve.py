from forensics_data import CARVE_BLOB

PNG_SIG = b"\x89PNG\r\n\x1a\n"


def carve_png(blob):
    pass


if __name__ == "__main__":
    png = carve_png(CARVE_BLOB)
    print("carved" if png else "nothing", len(png) if png else 0, "bytes")
