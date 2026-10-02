from modes import block_transform, ecb_encrypt, has_repeated_blocks, cbc_encrypt

KEY = bytes(range(16))
IV = bytes([7]) * 16


def test_ecb_block_multiple_length():
    out = ecb_encrypt(KEY, b"A" * 32)
    assert len(out) == 32


def test_ecb_repeats_identical_blocks():
    # Two identical 16-byte blocks must produce two identical cipher blocks.
    out = ecb_encrypt(KEY, b"YELLOW SUBMARINE" * 2)
    assert out[:16] == out[16:]


def test_has_repeated_blocks_detects_ecb():
    out = ecb_encrypt(KEY, b"YELLOW SUBMARINE" * 3)
    assert has_repeated_blocks(out)


def test_has_repeated_blocks_false_on_distinct():
    # Two different 16-byte blocks encrypt to two different cipher blocks.
    out = ecb_encrypt(KEY, b"block one.......block two.......")
    assert not has_repeated_blocks(out)


def test_has_repeated_blocks_direct():
    assert has_repeated_blocks(b"AAAAAAAAAAAAAAAABBBBBBBBBBBBBBBBAAAAAAAAAAAAAAAA")
    assert not has_repeated_blocks(b"AAAAAAAAAAAAAAAABBBBBBBBBBBBBBBB")


def test_cbc_hides_repeated_blocks():
    plain = b"YELLOW SUBMARINE" * 3
    out = cbc_encrypt(KEY, IV, plain)
    assert not has_repeated_blocks(out)


def test_cbc_first_block_uses_iv():
    # The first block is transform(key, p0 XOR iv): chaining starts from the IV.
    import hashlib
    p0 = b"YELLOW SUBMARINE"
    out = cbc_encrypt(KEY, IV, p0)
    mixed = bytes(pb ^ ivb for pb, ivb in zip(p0, IV))
    expected = hashlib.sha256(KEY + mixed).digest()[:16]
    assert out == expected


def test_cbc_length_matches_input():
    assert len(cbc_encrypt(KEY, IV, b"B" * 48)) == 48


def test_cbc_differs_from_ecb():
    plain = b"YELLOW SUBMARINE" * 2
    assert cbc_encrypt(KEY, IV, plain) != ecb_encrypt(KEY, plain)


def test_cbc_changes_with_iv():
    plain = b"YELLOW SUBMARINE" * 2
    other_iv = bytes([9]) * 16
    assert cbc_encrypt(KEY, IV, plain) != cbc_encrypt(KEY, other_iv, plain)
