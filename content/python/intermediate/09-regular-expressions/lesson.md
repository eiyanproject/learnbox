---
title: Regular expressions
summary: Find, extract, validate and rewrite text with patterns, groups and named captures.
order: 9
files: [patterns.py]
run: python -i patterns.py
hints:
  - "`find_hashtags`: `re.findall(r\"#(\\w+)\", text)` returns only the captured group."
  - "`parse_log_line`: strip the line first, then one pattern with named groups, e.g. `(?P<date>\\d{4}-\\d{2}-\\d{2}) (?P<level>[A-Z]+) (?P<message>.+)`, then `m.groupdict()` or `None` when `re.fullmatch` fails."
  - "`is_valid_username`: `re.fullmatch(r\"[a-z][a-z0-9_]{2,15}\", name) is not None`."
  - "`normalize_phone`: remove everything but digits with `re.sub(r\"\\D\", \"\", s)`, then turn a leading `0` into `62`."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **regular expression** (regex) | a small pattern language for describing the shape of text |
| **pattern** | a string where most characters match themselves and a few have special meanings |
| **raw string** (`r"..."`) | a string where backslashes are kept as typed, so they reach `re` untouched |
| **escape** | a backslash combination with a special meaning; `\.` matches a real full stop |
| **character class** | one character from a set: `[abc]`, `[a-z]`, `[^0-9]`, `\d`, `\w`, `\s` |
| **word character** | a letter, digit or `_` (`\w`) |
| **anchor** | `^` start, `$` end, `\b` word boundary: they match positions, not characters |
| **quantifier** | how many times the thing before it repeats: `*` `+` `?` `{3}` `{2,5}` |
| **greedy** / **lazy** | match as much as possible / as little as possible (a `?` after the quantifier) |
| **alternation** (`a\|b`) | either one |
| **match object** | what `search`, `match` and `fullmatch` return on success (`None` otherwise) |
| **span** | a match's start and end positions, end not included |
| **validation** | checking that the **whole** text has a shape; use `fullmatch` |
| **group** | a bracketed part of a pattern, numbered from 1; group 0 is the whole match |
| **named group** | `(?P<name>...)`, reached as `m["name"]` |
| **non-capturing group** | `(?:...)`: groups for a quantifier without capturing |
| **backreference** | `\1`, `\2` in a replacement: what that group matched |
| **pattern object** | a compiled pattern with the same methods, minus the pattern argument |
| **flag** | an option that changes matching, such as ignoring case |
| **parser** | a proper reader for a nested format, such as `json`; regexes handle nesting badly |
| **country code** | the international prefix of a phone number, `62` for Indonesia |
| **domain** | the part of an email address after `@`, such as `mail.co.id` |

### Python functions and methods

| Name | What it does |
|---|---|
| `import re` | the regular-expression module |
| `re.search(p, text)` | the first match anywhere |
| `re.match(p, text)` | a match only at the very start |
| `re.fullmatch(p, text)` | a match only if the pattern covers the whole text |
| `re.findall(p, text)` | a list of every match (or of the groups, if the pattern has them) |
| `re.sub(p, replacement, text)` | replaces every match; the replacement may be a function of the match |
| `re.split(p, text)` | splits wherever the pattern matches |
| `re.compile(p)` | a reusable pattern object |
| `m.group(n)`, `m[n]`, `m.groups()` | one group's text; the same, shorter; all groups as a tuple |
| `m.groupdict()` | the named groups as a dict |
| `re.IGNORECASE` (`re.I`) | ignore the difference between capitals and small letters |
| `re.VERBOSE` | allow spaces, newlines and `#` comments in a pattern |
| `re.M` | make `^` and `$` match at each line |
| `bool(x)`, `is not None` | test whether a match succeeded |
| `line.strip()` | removes the trailing newline before matching |

---

String methods handle fixed text well: `"ERROR" in line`, `s.split(",")`.
They struggle as soon as the text you want is described by its *shape*
rather than spelled out: "a date like 2026-09-18", "every word that starts
with #", "anything that looks like an email address". A **regular
expression** (regex for short) is a small pattern language for describing
such shapes, and Python's support for it is in the `re` module.

A pattern is a string where most characters stand for themselves (`cat`
matches the text "cat") and a few have special meanings (`\d` means "any
digit"). Always write patterns as **raw strings**, with an `r` in front:
`r"\d+"`. In a normal string, Python itself treats some backslash
combinations as escapes (`"\b"` is a backspace character), so the pattern
`re` receives would not be the one you typed. In a raw string, backslashes
reach `re` untouched.

## The essentials

| Pattern | Matches |
|---|---|
| `.` | any character except newline |
| `\d` `\w` `\s` | digit, word character (letter, digit, `_`), whitespace |
| `\D` `\W` `\S` | the opposites |
| `[abc]` `[a-z]` `[^0-9]` | one character from a set, a range, or not in a set |
| `^` `$` | start and end of the string (or line with `re.M`) |
| `*` `+` `?` | 0 or more, 1 or more, 0 or 1 |
| `{3}` `{2,5}` | exactly 3, between 2 and 5 |
| `a|b` | either |
| `(...)` | a capturing group |
| `\b` | a word boundary |

The first rows describe **one character** each. The **quantifiers** (`*`,
`+`, `?` and the braces) say how many times the thing immediately before them may
repeat. So `\d` matches one digit, `\d+` one or more digits in a row, and
`\d{4}` exactly four. Some patterns to read:

- `\d{4}-\d{2}-\d{2}`: four digits, a dash, two digits, a dash, two digits.
  A date such as `2026-09-18`.
- `[A-Z]+`: one or more capital letters, such as `ERROR`.
- `colou?r`: `colo`, an optional `u`, then `r`, so both `color` and `colour`.
- `\bcat\b`: `cat` as a whole word. `\b` matches no character at all; it
  marks the boundary between a word character and a non-word one, so this
  finds "cat" in "the cat sat" but not in "concatenate".

To match a special character literally, put a backslash before it: `\.` is
a real full stop, and `\$` a real dollar sign.

Quantifiers are **greedy**: they match as much as possible, then give back
only what they must for the rest of the pattern to fit. Adding `?` after a
quantifier makes it **lazy**, matching as little as possible instead:

```pycon
>>> import re
>>> re.findall(r"<.+>", "<b>bold</b>")      # greedy: one match, to the last >
['<b>bold</b>']
>>> re.findall(r"<.+?>", "<b>bold</b>")     # lazy: each tag on its own
['<b>', '</b>']
```

## The functions

```pycon
>>> re.search(r"\d+", "order 66 shipped")      # the first match anywhere
<re.Match object; span=(6, 8), match='66'>
>>> print(re.match(r"\d+", "order 66"))         # only at the start: None
None
>>> re.match(r"\d+", "66 orders")
<re.Match object; span=(0, 2), match='66'>
>>> re.fullmatch(r"\d{4}", "2026")             # the whole string must match
<re.Match object; span=(0, 4), match='2026'>
>>> re.findall(r"\d+", "3 cats, 12 dogs")
['3', '12']
>>> re.sub(r"\s+", " ", "too   many  spaces")
'too many spaces'
>>> re.split(r"[,;]\s*", "a, b;c")
['a', 'b', 'c']
```

What each one does:

- `search(pattern, text)` looks for the first match anywhere in the text.
- `match` only tries at the very start of the text.
- `fullmatch` succeeds only if the pattern covers the **whole** text.
- These three return a **match object** when they succeed, and `None` when
  they do not, so the usual test is `if m:` or `is not None`. In the match
  object, `span=(6, 8)` gives the start and end positions (end not
  included, as in slicing) and `match='66'` the matched text.
- `findall` returns a list of every match, as strings.
- `sub(pattern, replacement, text)` replaces every match and returns the new
  string.
- `split` splits the text wherever the pattern matches, like `str.split`
  but with a pattern as the separator.

`re.search` finds a match anywhere; use `re.fullmatch` for **validation**,
or text that merely *contains* a valid part will pass:

```pycon
>>> bool(re.search(r"\d+", "abc123"))       # found some digits: "valid"?!
True
>>> bool(re.fullmatch(r"\d+", "abc123"))    # not only digits: rejected
False
```

`fullmatch` is also safer than wrapping a pattern in `^...$`, because `$`
matches immediately before a newline at the end of the text as well as at the very
end. `re.search(r"^[a-z]+$", "ana\n")` succeeds; `re.fullmatch` correctly
rejects it.

## Groups

Round brackets in a pattern make a **group**. The match object can then
give you each bracketed part separately, which is how you pull pieces out of
text, not only find it:

```pycon
>>> m = re.search(r"(\d{4})-(\d{2})-(\d{2})", "due 2026-09-18")
>>> m.group(0)        # the whole match
'2026-09-18'
>>> m.group(1)
'2026'
>>> m.groups()
('2026', '09', '18')
```

Groups are numbered from 1 in the order their opening brackets appear;
group 0 is always the whole match.

With groups in the pattern, `findall` returns the groups instead of whole
matches. With one group, you get a list of that group's text:

```pycon
>>> re.findall(r"(\w+)@", "ana@x.io, bo@y.io")
['ana', 'bo']
```

Named groups read far better than numbers. `(?P<name>...)` gives a group a
name, and the match object can then be indexed by it:

```pycon
>>> m = re.match(r"(?P<user>\w+)@(?P<host>[\w.]+)", "ana@example.com")
>>> m["user"], m["host"]
('ana', 'example.com')
>>> m.groupdict()
{'user': 'ana', 'host': 'example.com'}
```

`groupdict()` returns all the named groups as a dict, which is often exactly
the shape you want to return.

Sometimes you need brackets only to apply a quantifier or `|` to several
characters at once, not to capture anything. `(?:...)` groups without
capturing, so it does not show up in `groups()` or `findall`:

```pycon
>>> re.findall(r"(?:ab)+", "ababab abx")      # "ab" repeated, as one unit
['ababab', 'ab']
```

## Substitution with groups

In `sub`, the replacement can refer back to the groups: `\1` is replaced by
whatever group 1 matched, `\2` by group 2, and so on. That lets you
rearrange text. Here a day/month/year date is turned into year-month-day:

```pycon
>>> re.sub(r"(\d{2})/(\d{2})/(\d{4})", r"\3-\2-\1", "18/09/2026")
'2026-09-18'
>>> re.sub(r"\d+", lambda m: str(int(m[0]) * 2), "3 and 4")
'6 and 8'
```

The replacement can also be a function. `sub` calls it with each match
object and uses whatever string it returns, which allows any calculation:
here every number is doubled. (`m[0]` is a shorter way to write
`m.group(0)`.)

## Compile and flags

`re.compile(pattern)` turns a pattern into a **pattern object** once. It has
the same methods (`search`, `findall`, `sub` and so on) without the pattern
argument. Compiling a pattern that is used many times, and giving it a name,
makes the code easier to read; Python also caches recent patterns itself, so
the speed difference is small.

**Flags** change how a pattern matches. `re.IGNORECASE` (or `re.I`) ignores
the difference between capital and small letters:

```pycon
>>> text = "Error on 2026-09-18, retried 2026-09-19: error again"
>>> DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
>>> DATE.findall(text)
['2026-09-18', '2026-09-19']
>>> re.findall(r"error", text, flags=re.IGNORECASE)
['Error', 'error']
```

`re.VERBOSE` lets you spread a complex pattern over several lines with
comments. Spaces and newlines in the pattern are then ignored (write `\ ` or
`[ ]` for a real space), and `#` starts a comment:

```pycon
>>> PHONE = re.compile(r"""
...     (\d{3})    # area code
...     [-\s]?     # optional separator
...     (\d{4})    # number
... """, re.VERBOSE)
>>> PHONE.fullmatch("021-5550").groups()
('021', '5550')
```

## When not to

Regular expressions are dense and hard to read back, so do not reach for
one when a plain method does the job. `str.startswith`, `in`, `split` and
`replace` are clearer for fixed text. And do not parse HTML or JSON with
regexes: those formats nest, and nesting is something patterns handle
badly. Use a parser, such as the `json` module you met in the Files lesson.

## Your turn

In `patterns.py`:

- `find_hashtags(text)`: the tags without `#`. A tag is a `#` followed
  directly by one or more word characters (letters, digits, `_`), wherever it
  appears, even in the middle of a word: `"#python and #re_2, not a#b?"`
  gives `["python", "re_2", "b"]`. No tags gives `[]`.
- `parse_log_line(line)`: for `"2026-09-18 ERROR disk full"` return
  `{"date": "2026-09-18", "level": "ERROR", "message": "disk full"}`. The
  date is in exactly that year-month-day form, the level is one or more
  capital letters, and the message is everything after the level's space;
  it must not be empty. Return `None` for lines that do not have that shape,
  such as `"18-09-2026 ERROR x"` (date the wrong way round), a lower-case
  level, or `"2026-09-18 WARN"` (no message). A line may end with a newline
  character, which is not part of the message.
- `is_valid_username(name)`: `True` when the name is 3 to 16 characters long,
  uses only lower-case letters, digits and `_`, and starts with a letter.
  `"ana_99"` is valid; `"9lives"` (starts with a digit), `"Al"` (upper case,
  and too short), `"ana-b"` (a hyphen) and `"ana\n"` (a newline is not
  allowed either) are not.
- `normalize_phone(s)`: keep only the digits, and if the result starts with
  `0`, replace that one leading `0` with the country code `62`:
  `"0812-3456 789"` gives `"628123456789"`, `"+62 812 3456 789"` gives the
  same (it already starts with 62), and `"8100"` stays `"8100"` (the zeros
  in the middle are not leading).
- `mask_emails(text)`: replace the part before `@` of every email with `***`:
  `"mail ana.b@x.io now"` gives `"mail ***@x.io now"`. The part before `@`
  may contain letters, digits, `_`, `.`, `+` and `-`; the part after it is a
  domain with at least one dot, such as `mail.co.id`. An `@` with spaces
  around it is not an email and is left alone.
