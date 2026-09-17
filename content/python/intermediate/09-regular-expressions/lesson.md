---
title: Regular expressions
summary: Find, extract, validate and rewrite text with patterns, groups and named captures.
order: 9
files: [patterns.py]
run: python -i patterns.py
hints:
  - "`find_hashtags`: `re.findall(r\"#(\\w+)\", text)` returns just the captured group."
  - "`parse_log_line`: one pattern with named groups, e.g. `(?P<date>\\d{4}-\\d{2}-\\d{2}) (?P<level>[A-Z]+) (?P<message>.*)`, then `m.groupdict()` or `None` when `re.fullmatch` fails."
  - "`is_valid_username`: `re.fullmatch(r\"[a-z][a-z0-9_]{2,15}\", name) is not None`."
  - "`normalize_phone`: remove everything but digits with `re.sub(r\"\\D\", \"\", s)`, then turn a leading `0` into `62`."
---

A **regular expression** is a small pattern language for matching text.
Python's is in the `re` module. Always write patterns as raw strings (`r"..."`)
so backslashes reach `re` untouched.

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

Quantifiers are **greedy** (match as much as possible). Add `?` for lazy:
`<.+?>` matches one tag, `<.+>` runs to the last `>` on the line.

## The functions

```python
import re

re.search(r"\d+", "order 66 shipped")      # first match anywhere -> Match or None
re.match(r"\d+", "66 orders")              # only at the start
re.fullmatch(r"\d{4}", "2026")             # the whole string must match
re.findall(r"\d+", "3 cats, 12 dogs")      # ['3', '12']
re.sub(r"\s+", " ", "too   many  spaces")  # 'too many spaces'
re.split(r"[,;]\s*", "a, b;c")             # ['a', 'b', 'c']
```

`re.search` finds a match anywhere; use `re.fullmatch` for **validation**, or
`"abc123"` will happily "match" a digits-only pattern.

## Groups

```python
m = re.search(r"(\d{4})-(\d{2})-(\d{2})", "due 2026-09-18")
m.group(0)        # '2026-09-18'  the whole match
m.group(1)        # '2026'
m.groups()        # ('2026', '09', '18')
```

With groups in the pattern, `findall` returns the groups instead of whole matches.

Named groups read far better:

```python
m = re.match(r"(?P<user>\w+)@(?P<host>[\w.]+)", "ana@example.com")
m["user"], m["host"]
m.groupdict()     # {'user': 'ana', 'host': 'example.com'}
```

`(?:...)` groups without capturing.

## Substitution with groups

```python
re.sub(r"(\d{2})/(\d{2})/(\d{4})", r"\3-\2-\1", "18/09/2026")   # '2026-09-18'
re.sub(r"\d+", lambda m: str(int(m[0]) * 2), "3 and 4")        # '6 and 8'
```

## Compile and flags

```python
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
DATE.findall(text)
re.findall(r"error", text, flags=re.IGNORECASE)
```

`re.VERBOSE` lets you spread a complex pattern over lines with comments.

## When not to

`str.startswith`, `in`, `split` and `replace` are clearer for fixed text. Do not
parse HTML or JSON with regexes; use a parser.

## Your turn

In `patterns.py`:

- `find_hashtags(text)`: the tags without `#`: `"#python and #re_2"` gives `["python", "re_2"]`
- `parse_log_line(line)`: for `"2026-09-18 ERROR disk full"` return
  `{"date": "2026-09-18", "level": "ERROR", "message": "disk full"}`; return `None`
  for lines that do not have that shape
- `is_valid_username(name)`: 3 to 16 characters, lower-case letters, digits and
  `_`, starting with a letter
- `normalize_phone(s)`: keep only digits, and replace a leading `0` with `62`:
  `"0812-3456 789"` gives `"628123456789"`
- `mask_emails(text)`: replace the part before `@` of every email with `***`:
  `"mail ana.b@x.io now"` gives `"mail ***@x.io now"`
