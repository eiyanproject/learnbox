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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **HTML** | the language web pages are written in: text with tags such as `<div>` and `<p>` |
| **tag** (element) | a piece of HTML in angle brackets; `<div>...</div>` opens and closes one |
| **attribute** | a setting inside a tag: `class='comment'` |
| **JavaScript** | the programming language browsers run inside pages |
| **`<script>`** | the tag whose contents the browser runs as JavaScript |
| **cross-site scripting** (XSS) | user input placed into a page as HTML, so it runs as code in other people's browsers |
| **stored XSS** | the input is saved (a comment, a profile) and served to everyone who views it |
| **reflected XSS** | the input comes from the link itself (a search term) and is echoed straight back |
| **untrusted input** | anything a user, or an attacker, could have typed or sent |
| **session cookie** | the cookie that keeps you logged in; a script on the page can often read it |
| **`document.cookie`** | in JavaScript, the page's cookies |
| **`steal(...)`** | a made-up function name in this lesson's payload, standing for "send this to the attacker" |
| **escaping** (output encoding) | replacing characters that mean something in HTML with harmless codes |
| **HTML entity** | such a code: `&lt;` shows as `<`, `&gt;` as `>`, `&amp;` as `&` |
| **context** | where in the page the value goes: element text, an attribute, a script, a URL |
| **event handler** | an attribute like `onclick` whose value is JavaScript |
| **`javascript:` URL** | a link address that runs code instead of opening a page |
| **auto-escaping template** | a page-building tool that escapes every value unless told not to |
| **Content Security Policy** (CSP) | a response header telling the browser which scripts it may run; a second layer, not the fix |
| **HttpOnly** | a cookie setting that hides the cookie from JavaScript |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python xss.py` | runs your program: renders the payload unsafely and safely |

### Python names

| Name | What it does |
|---|---|
| `import html` | loads Python's HTML helpers |
| `html.escape(text)` | `text` with `<`, `>`, `&`, `"` and `'` turned into entities |
| `f"<div class='comment'>{text}</div>"` | an f-string: `{text}` is replaced by the value of `text` |
| `render_unsafe(text)` | given to you: puts `text` into the page **without** escaping |

---

A comment box, a search page that repeats your search term, a profile field
shown to other people: anywhere a site puts **user input into a page**,
**cross-site scripting** (XSS) is possible. If the input goes into the HTML
without being escaped, an attacker's input stops being text and becomes part
of the page's code, running in the browser of everyone who views it.

## How a page is built

A web page is **HTML**: text with **tags** in angle brackets. `<div>` starts a
box and `</div>` ends it; `<b>` makes text bold. One tag is special:
everything between `<script>` and `</script>` is **JavaScript**, and the
browser runs it.

A site often builds HTML with a template like this:

```python
def render(comment):
    return f"<div class='comment'>{comment}</div>"
```

For the comment `Nice post!`, the page gets
`<div class='comment'>Nice post!</div>`. Fine.

## The attack

Now post this as the comment:

```text
<script>steal(document.cookie)</script>
```

The page served to every visitor now contains:

```text
unsafe: <div class='comment'><script>steal(document.cookie)</script></div>
```

The browser cannot know that the script came from a comment. It sees a script
tag and runs it, **inside the victim's logged-in session**. A real script would
read the session cookie (`document.cookie`), send it to the attacker (`steal`
is a stand-in name here), make requests as the victim, or change what the page
shows.

Because the comment is saved and shown to everyone, one post reaches every
viewer: that is **stored XSS**. In **reflected XSS**, the input comes from a
crafted link, for example a search page that prints back the search term, and
hits whoever clicks the link. The cause and the fix are the same.

You will write the payload and see it survive the unsafe renderer as a live
script tag.

## The defence: escape on output

Before putting any untrusted value into HTML, replace the characters that mean
something in HTML with harmless **entities**:

| Character | becomes |
|---|---|
| `<` | `&lt;` |
| `>` | `&gt;` |
| `&` | `&amp;` |
| `"` | `&quot;` |
| `'` | `&#x27;` |

The browser shows `&lt;` as a `<` on screen, but never treats it as the start
of a tag. So `<script>` arrives as the text `&lt;script&gt;`, which the browser
displays instead of running. Python's `html.escape` does exactly this:

```pycon
>>> import html
>>> html.escape("<script>steal(document.cookie)</script>")
'&lt;script&gt;steal(document.cookie)&lt;/script&gt;'
>>> html.escape("Tom & Jerry's \"show\"")
'Tom &amp; Jerry&#x27;s &quot;show&quot;'
```

The second example shows that ordinary text still displays correctly:
escaping changes only the special characters.

The principle is the one from SQL injection: keep untrusted input as **data**,
never code. There the boundary was the query; here it is the page.

### Escaping depends on where the value goes

`html.escape` is right for text inside an HTML element, or inside a **quoted**
attribute. It is **not** enough in other **contexts**:

- inside a `<script>` block;
- in an **event handler** attribute such as `onclick`;
- as a link address in `href`: the value `javascript:alert(1)` contains no
  character that `html.escape` would change, yet clicking it runs code.

Each of those needs its own encoding, or better, keeping untrusted data out of
them altogether. OWASP's XSS Prevention Cheat Sheet lists the rules for each
context.

Real applications rely on **auto-escaping templates**, which escape every
value unless you deliberately turn it off, and add a **Content Security
Policy** header and **HttpOnly** cookies as further layers. Escaping on output
is the foundation under all of them.

## Your turn

`render_unsafe(text)` is given to you. In `xss.py`:

- `xss_payload()`: a string that appears as a working `<script>` element in
  the output of `render_unsafe`.
- `render_safe(text)`: the same `<div class='comment'>...</div>`, but with the
  text escaped, so a script payload shows as harmless text while ordinary
  comments still display normally.

Run it:

```text
unsafe: <div class='comment'><script>steal(document.cookie)</script></div>
safe:   <div class='comment'>&lt;script&gt;steal(document.cookie)&lt;/script&gt;</div>
```

## Check yourself

1. Why does the browser run the script in the comment?
   *It cannot tell page code from user input that was put in without
   escaping.*
2. What is the difference between stored and reflected XSS?
   *Stored is saved and shown to everyone; reflected comes from a crafted
   link.*
3. What does `html.escape("<b>")` give?
   *`'&lt;b&gt;'`.*
4. Why is `html.escape` not enough for a value placed in `href`?
   *A `javascript:` address has no characters it would change.*
5. Is a Content Security Policy a replacement for escaping?
   *No: it is a second layer.*
