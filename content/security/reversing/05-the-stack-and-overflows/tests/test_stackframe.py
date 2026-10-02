from stackframe import offset_to_return, overflows_buffer, reaches_return_address


def test_offset_to_return():
    assert offset_to_return(64) == 72
    assert offset_to_return(16) == 24


def test_offset_small_buffer():
    assert offset_to_return(0) == 8


def test_overflow_true():
    assert overflows_buffer(65, 64)


def test_overflow_false_when_exact():
    assert not overflows_buffer(64, 64)


def test_overflow_false_when_short():
    assert not overflows_buffer(10, 64)


def test_reaches_return_true():
    # 73 bytes: 64 buffer + 8 saved bp + 1 into the return address.
    assert reaches_return_address(73, 64)


def test_reaches_return_false_in_saved_bp():
    # 72 bytes fills buffer and saved bp exactly, not yet the return address.
    assert not reaches_return_address(72, 64)


def test_reaches_return_false_within_buffer():
    assert not reaches_return_address(30, 64)


def test_overflow_but_not_reaching_return():
    # Overflows the buffer (into the saved base pointer) without reaching return.
    assert overflows_buffer(68, 64)
    assert not reaches_return_address(68, 64)
