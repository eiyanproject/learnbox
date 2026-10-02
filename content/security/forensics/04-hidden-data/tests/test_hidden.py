from hidden import embed_lsb, data_after_iend, extract_lsb
from forensics_data import CLEAN_PNG, STEGO_PNG


def test_clean_png_has_nothing_after_iend():
    assert data_after_iend(CLEAN_PNG) == b""


def test_stego_png_trailing_data_found():
    assert data_after_iend(STEGO_PNG) == b"SECRET: the meeting is at midnight"


def test_data_after_iend_no_png():
    assert data_after_iend(b"not a png at all") == b""


def test_extract_simple_message():
    stego = embed_lsb(bytes(500), "attack at dawn")
    assert extract_lsb(stego) == "attack at dawn"


def test_extract_stops_at_terminator():
    # Bytes after the null terminator must not bleed into the message.
    stego = embed_lsb(bytes(500), "short")
    assert extract_lsb(stego) == "short"


def test_extract_from_nonzero_carrier():
    carrier = bytes(range(256)) * 4
    stego = embed_lsb(carrier, "hidden!")
    assert extract_lsb(stego) == "hidden!"


def test_extract_empty_message():
    stego = embed_lsb(bytes(50), "")
    assert extract_lsb(stego) == ""


def test_embedding_barely_changes_the_carrier():
    # Only low bits move: every byte stays within 1 of the original.
    carrier = bytes([128]) * 200
    stego = embed_lsb(carrier, "x")
    assert all(abs(a - b) <= 1 for a, b in zip(carrier, stego))
