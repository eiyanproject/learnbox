from codes import xor_bytes, looks_like_text, break_single_byte_xor


def test_xor_is_its_own_inverse():
    data = b"attack at dawn"
    once = xor_bytes(data, b"K")
    assert xor_bytes(once, b"K") == data


def test_xor_repeats_a_multibyte_key():
    out = xor_bytes(b"\x00\x00\x00\x00", b"\x01\x02")
    assert out == b"\x01\x02\x01\x02"


def test_xor_returns_bytes():
    assert isinstance(xor_bytes(b"hi", b"x"), bytes)


def test_xor_against_zero_key_is_identity():
    assert xor_bytes(b"hello", b"\x00") == b"hello"


def test_looks_like_text_accepts_a_sentence():
    assert looks_like_text(b"meet me at dawn")


def test_looks_like_text_rejects_binary_noise():
    assert not looks_like_text(bytes([0, 1, 2, 255, 254, 128, 9]))


def test_looks_like_text_rejects_text_without_spaces():
    assert not looks_like_text(b"nospacesanywherehere")


def test_looks_like_text_rejects_empty():
    assert not looks_like_text(b"")


def test_break_recovers_the_key_and_message():
    cipher = xor_bytes(b"meet me at the bridge", b"Q")
    key, plain = break_single_byte_xor(cipher)
    assert key == ord("Q")
    assert plain == "meet me at the bridge"


def test_break_recovers_a_different_message():
    cipher = xor_bytes(b"the password is swordfish", b"\x2a")
    _, plain = break_single_byte_xor(cipher)
    assert plain == "the password is swordfish"


def test_break_returns_a_str_plaintext():
    cipher = xor_bytes(b"hello there friend", b"z")
    _, plain = break_single_byte_xor(cipher)
    assert isinstance(plain, str)
