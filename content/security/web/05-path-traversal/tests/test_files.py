import os
import pytest
from files import serve_vulnerable, traversal_payload, serve_safe


def build_site(tmp_path):
    # web root with one legitimate file, and a secret ONE LEVEL ABOVE it.
    root = tmp_path / "www"
    root.mkdir()
    (root / "index.html").write_text("home page")
    (tmp_path / "secret.txt").write_text("TOPSECRET")
    return str(root)


def test_payload_escapes_the_root(tmp_path):
    root = build_site(tmp_path)
    assert serve_vulnerable(root, traversal_payload()) == "TOPSECRET"


def test_safe_serves_a_legitimate_file(tmp_path):
    root = build_site(tmp_path)
    assert serve_safe(root, "index.html") == "home page"


def test_safe_blocks_the_payload(tmp_path):
    root = build_site(tmp_path)
    with pytest.raises(ValueError):
        serve_safe(root, traversal_payload())


def test_safe_blocks_a_deep_traversal(tmp_path):
    root = build_site(tmp_path)
    with pytest.raises(ValueError):
        serve_safe(root, "../../../../etc/hostname")


def test_safe_blocks_an_absolute_path(tmp_path):
    root = build_site(tmp_path)
    with pytest.raises(ValueError):
        serve_safe(root, "/etc/hostname")
