from perms import mode_to_rwx, is_world_writable, is_too_open_for_secret, tighten


def test_rwx_644():
    assert mode_to_rwx(0o644) == "rw-r--r--"


def test_rwx_640():
    assert mode_to_rwx(0o640) == "rw-r-----"


def test_rwx_755():
    assert mode_to_rwx(0o755) == "rwxr-xr-x"


def test_rwx_600():
    assert mode_to_rwx(0o600) == "rw-------"


def test_rwx_777():
    assert mode_to_rwx(0o777) == "rwxrwxrwx"


def test_rwx_000():
    assert mode_to_rwx(0o000) == "---------"


def test_world_writable_true():
    assert is_world_writable(0o666)
    assert is_world_writable(0o777)


def test_world_writable_false():
    assert not is_world_writable(0o644)
    assert not is_world_writable(0o660)


def test_secret_leak_when_group_can_read():
    assert is_too_open_for_secret(0o640)


def test_secret_leak_when_world_can_read():
    assert is_too_open_for_secret(0o644)


def test_no_leak_when_owner_only():
    assert not is_too_open_for_secret(0o600)
    assert not is_too_open_for_secret(0o700)


def test_tighten_strips_group_and_other():
    assert tighten(0o644) == 0o600
    assert tighten(0o777) == 0o700


def test_tighten_leaves_owner_only_alone():
    assert tighten(0o600) == 0o600


def test_tighten_makes_a_secret_safe():
    leaky = 0o644
    assert is_too_open_for_secret(leaky)
    assert not is_too_open_for_secret(tighten(leaky))
