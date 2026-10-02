from meta import parse_chunks, dimensions, text_metadata
from png_data import SAMPLE_PNG


def test_chunks_start_with_ihdr_end_with_iend():
    chunks = parse_chunks(SAMPLE_PNG)
    assert chunks[0][0] == "IHDR"
    assert chunks[-1][0] == "IEND"


def test_chunks_include_text():
    types = [c[0] for c in parse_chunks(SAMPLE_PNG)]
    assert types.count("tEXt") == 2


def test_dimensions():
    assert dimensions(SAMPLE_PNG) == (2, 2)


def test_text_metadata_author():
    assert text_metadata(SAMPLE_PNG)["Author"] == "Jane Doe"


def test_text_metadata_leaks_location():
    # The comment field carries GPS coordinates - exactly the privacy leak.
    assert "51.5074" in text_metadata(SAMPLE_PNG)["Comment"]


def test_text_metadata_is_a_dict():
    meta = text_metadata(SAMPLE_PNG)
    assert set(meta.keys()) == {"Author", "Comment"}


def test_iend_has_empty_data():
    chunks = dict((t, b) for t, b in parse_chunks(SAMPLE_PNG))
    assert chunks["IEND"] == b""
