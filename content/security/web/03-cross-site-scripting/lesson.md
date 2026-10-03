---
title: Cross-site scripting
summary: When a page echoes user input into HTML without escaping it, that input becomes code in every visitor's browser - and escaping is the fix.
order: 3
files: [xss.py]
run: python xss.py
hints:
  - "`xss_payload`: return a string that, dropped into HTML unescaped, is an executing script - a `<script>...</script>` element is the simplest."
  - "`render_unsafe` is provided and just wraps your text in a div. Your payload must appear in its output with the angle brackets intact."
  - "`render_safe`: run the text through `html.escape` before placing it, so `<` becomes `&lt;` and the browser shows it as text instead of running it."
  - "A good `render_safe` still displays ordinary comments correctly - escaping changes only the characters that have meaning in HTML."
---

A comment box, a search page that echoes your term, a profile field shown back
to others - anywhere a site puts **user input into a page**, there is a chance
for **cross-site scripting** (XSS). If the input is placed into the HTML without
being escaped, an attacker's input stops being text and becomes part of the
page's code, running in the browser of everyone who views it.

## The attack

Suppose a comment is rendered like this:

```python
def render(comment):
    return f"<div class='comment'>{comment}</div>"
```

Post a comment of `<script>steal(document.cookie)</script>` and the page served
to every other visitor contains a live script tag. It runs in their session,
with their cookies, as them - stealing session tokens, making requests on their
behalf, defacing the page. Because it is **stored** and served to others, one
post hits every viewer. (The reflected variant bounces off a search page via a
crafted link; same cause, same fix.)

You will write a payload that survives the unsafe renderer as executable markup.

## The defence

**Escape on output.** Before putting any untrusted value into HTML, convert the
characters that have meaning in HTML into their harmless entities:

| | becomes |
|---|---|
| `<` | `&lt;` |
| `>` | `&gt;` |
| `&` | `&amp;` |
| `"` | `&quot;` |
| `'` | `&#x27;` |

Now `<script>` arrives in the page as the literal text `&lt;script&gt;`, which
the browser displays rather than executes. Python's `html.escape` does exactly
this:

```pycon
>>> import html
>>> html.escape("<script>steal(document.cookie)</script>")
'&lt;script&gt;steal(document.cookie)&lt;/script&gt;'
>>> html.escape("Tom & Jerry's \"show\"")
'Tom &amp; Jerry&#x27;s &quot;show&quot;'
```

 The principle mirrors SQL injection: keep untrusted input as **data**, not
code - there the boundary was the query, here it is the page.

Escaping is **context-dependent**, and `html.escape` is right for text placed in
an HTML element or a quoted attribute. It is not enough inside a `<script>`
block, an event handler like `onclick`, or a URL in `href` - a value of
`javascript:alert(1)` contains no characters it would change. Those contexts
need their own encoding, or better, keeping untrusted data out of them entirely.

(Real applications lean on auto-escaping template engines and a Content Security
Policy as a second layer, but escaping on output is the foundation under both.)

## Your turn

`render_unsafe(text)` is provided. In `xss.py`:

- `xss_payload()` - a string that appears as an executable `<script>` element in
  the output of `render_unsafe`
- `render_safe(text)` - the same rendering, but with the text escaped so a
  script payload is shown as inert text while ordinary comments still display
