import html


def render_unsafe(text):
    # VULNERABLE: user text goes straight into the page.
    return f"<div class='comment'>{text}</div>"


def xss_payload():
    # Dropped into the page unescaped, this is a live script element - it runs
    # in the browser of whoever views the comment.
    return "<script>steal(document.cookie)</script>"


def render_safe(text):
    # html.escape turns the HTML-significant characters into entities, so the
    # payload arrives as text the browser prints rather than markup it runs.
    return f"<div class='comment'>{html.escape(text)}</div>"


if __name__ == "__main__":
    p = xss_payload()
    print("unsafe:", render_unsafe(p))
    print("safe:  ", render_safe(p))
