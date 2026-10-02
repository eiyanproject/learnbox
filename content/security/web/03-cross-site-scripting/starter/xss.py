import html


def render_unsafe(text):
    # VULNERABLE: user text goes straight into the page.
    return f"<div class='comment'>{text}</div>"


def xss_payload():
    # Return a string that becomes an executing <script> in render_unsafe.
    pass


def render_safe(text):
    # Escape the text so a script payload is shown, not run.
    pass


if __name__ == "__main__":
    p = xss_payload()
    print("unsafe:", render_unsafe(p))
    print("safe:  ", render_safe(p))
