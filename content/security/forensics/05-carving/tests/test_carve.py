from carve import carve_png
from forensics_data import CARVE_BLOB, CLEAN_PNG


def test_carves_the_embedded_png():
    assert carve_png(CARVE_BLOB) == CLEAN_PNG


def test_carved_file_is_a_valid_png():
    out = carve_png(CARVE_BLOB)
    assert out.startswith(b"\x89PNG\r\n\x1a\n")
    assert out.rstrip().endswith(b"IEND" + out[-4:])


def test_none_when_no_signature():
    assert carve_png(b"just some random bytes with no image") is None


def test_none_when_no_iend():
    # A signature but a truncated file - no footer to close it.
    assert carve_png(b"\x89PNG\r\n\x1a\n and then nothing useful") is None


def test_carves_png_with_no_surrounding_junk():
    assert carve_png(CLEAN_PNG) == CLEAN_PNG


def test_ignores_leading_junk():
    blob = b"\xff" * 100 + CLEAN_PNG
    assert carve_png(blob) == CLEAN_PNG
