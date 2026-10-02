from filetype import identify, extension_mismatch


def test_identify_png():
    assert identify(b"\x89PNG\r\n\x1a\n....") == "png"


def test_identify_elf():
    assert identify(b"\x7fELF\x02\x01\x01") == "elf"


def test_identify_pdf():
    assert identify(b"%PDF-1.7") == "pdf"


def test_identify_jpeg():
    assert identify(b"\xff\xd8\xff\xe0") == "jpeg"


def test_identify_zip():
    assert identify(b"PK\x03\x04") == "zip"


def test_identify_unknown():
    assert identify(b"random bytes here") == "unknown"


def test_mismatch_elf_as_jpg():
    assert extension_mismatch("photo.jpg", b"\x7fELF\x02")


def test_mismatch_png_as_pdf():
    assert extension_mismatch("report.pdf", b"\x89PNG\r\n\x1a\n")


def test_no_mismatch_when_correct():
    assert not extension_mismatch("real.png", b"\x89PNG\r\n\x1a\n")
    assert not extension_mismatch("doc.pdf", b"%PDF-1.4")


def test_jpg_and_jpeg_both_accepted():
    assert not extension_mismatch("a.jpeg", b"\xff\xd8\xff")
    assert not extension_mismatch("a.jpg", b"\xff\xd8\xff")


def test_unknown_type_is_not_flagged():
    # If we cannot identify the bytes, we cannot claim a mismatch.
    assert not extension_mismatch("x.png", b"not a known format")
