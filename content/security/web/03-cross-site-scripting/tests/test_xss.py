from xss import render_unsafe, xss_payload, render_safe


def test_payload_executes_in_the_unsafe_renderer():
    out = render_unsafe(xss_payload())
    # The script tag survives intact - that is what makes it run in a browser.
    assert "<script>" in out


def test_payload_is_actually_a_script():
    assert "<script>" in xss_payload()


def test_safe_renderer_neutralises_the_payload():
    out = render_safe(xss_payload())
    assert "<script>" not in out


def test_safe_renderer_escapes_the_angle_brackets():
    out = render_safe(xss_payload())
    assert "&lt;script&gt;" in out


def test_safe_renderer_still_shows_normal_text():
    out = render_safe("I love this post")
    assert "I love this post" in out


def test_safe_renderer_escapes_ampersand():
    assert "&amp;" in render_safe("Tom & Jerry")


def test_safe_renderer_keeps_its_wrapper():
    # The div is the page's own markup and must remain; only the input is escaped.
    assert render_safe("hi").startswith("<div class='comment'>")


def test_plain_text_is_unchanged_apart_from_wrapping():
    assert render_safe("hello world") == "<div class='comment'>hello world</div>"
