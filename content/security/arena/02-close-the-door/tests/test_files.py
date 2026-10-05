import pytest

from files import Forbidden, resolve

BASE = "/srv/files"


@pytest.mark.parametrize(
    "requested, full",
    [
        ("report.txt", "/srv/files/report.txt"),
        ("2026/q1/notes.txt", "/srv/files/2026/q1/notes.txt"),
        ("a/../b.txt", "/srv/files/b.txt"),
        ("./a//b.txt", "/srv/files/a/b.txt"),
        ("a/b/../../c.txt", "/srv/files/c.txt"),
        ("..hidden", "/srv/files/..hidden"),
        ("notes..txt", "/srv/files/notes..txt"),
    ],
)
def test_honest_requests_still_work(requested, full):
    assert resolve(BASE, requested) == full


@pytest.mark.parametrize(
    "requested",
    [
        "../etc/passwd",
        "../../etc/passwd",
        "a/../../secret",
        "a/b/../../../secret",
        "./../x",
        "..",
        "../",
    ],
)
def test_climbing_out_is_refused(requested):
    with pytest.raises(Forbidden):
        resolve(BASE, requested)


def test_a_folder_with_a_similar_name_is_still_outside():
    with pytest.raises(Forbidden):
        resolve(BASE, "../files-private/x")
    with pytest.raises(Forbidden):
        resolve(BASE, "../files2")


@pytest.mark.parametrize("requested", ["/etc/passwd", "/srv/files/report.txt", "//etc/passwd"])
def test_absolute_paths_are_refused(requested):
    with pytest.raises(Forbidden):
        resolve(BASE, requested)


@pytest.mark.parametrize("requested", ["", ".", "./", "a/..", "a/../"])
def test_the_folder_itself_is_not_a_file(requested):
    with pytest.raises(Forbidden):
        resolve(BASE, requested)


@pytest.mark.parametrize("requested", ["a\\b.txt", "..\\secret", "report.txt\x00.png", "\x00"])
def test_backslashes_and_nul_are_refused(requested):
    with pytest.raises(Forbidden):
        resolve(BASE, requested)


def test_a_base_with_a_trailing_slash():
    assert resolve("/srv/files/", "report.txt") == "/srv/files/report.txt"
    with pytest.raises(Forbidden):
        resolve("/srv/files/", "../files-private/x")


def test_another_base():
    assert resolve("/var/www/site", "img/logo.png") == "/var/www/site/img/logo.png"
    with pytest.raises(Forbidden):
        resolve("/var/www/site", "../site.bak/db.sql")


def test_forbidden_is_an_exception_of_its_own():
    assert issubclass(Forbidden, Exception)
    assert not issubclass(Forbidden, (ValueError, OSError))
