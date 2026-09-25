---
title: Text processing
summary: Cleaning up text that people typed, pulling numbers out of it, and the regular expression functions worth knowing.
order: 3
files: [normalise_name.m, extract_numbers.m, initials.m]
run: octave --no-gui --quiet --eval "disp(initials('ada  lovelace king'))"
hints:
  - "`regexprep(s, '\\s+', ' ')` collapses every run of whitespace to one space. Trim first, or you keep the outer ones."
  - "`regexp(s, pattern, 'match')` returns a cell array of the matching text."
  - "A number is roughly `-?\\d+(\\.\\d+)?` - an optional minus, digits, and optionally a dot and more digits."
  - "`strsplit` on whitespace, take `p(1)` of each part, `upper` it, and `strjoin` with '.'."
---

## The everyday functions

| | |
|---|---|
| `strtrim(s)` | drop leading and trailing whitespace |
| `lower` / `upper` | case |
| `strrep(s, a, b)` | literal replacement, no patterns |
| `strsplit` / `strjoin` | text to pieces and back |
| `strcmp` / `strcmpi` | compare, exactly or ignoring case |
| `contains` / `startsWith` / `endsWith` | membership |
| `sprintf` | build formatted text |

Use `strcmp`, not `==`. On char arrays `==` compares **element by element** and
needs both sides the same length — `'abc' == 'abd'` gives `[1 1 0]`, and
comparing different lengths is an error.

## Regular expressions

```matlab
regexp(s, pattern, 'match')     % the matching text, as a cell array
regexp(s, pattern, 'once')      % just the first, as char
regexp(s, pattern, 'tokens')    % the capture groups
regexprep(s, pattern, repl)     % replace
```

Enough of the syntax to be useful:

| | |
|---|---|
| `\d` | a digit; `\s` whitespace; `\w` word character |
| `+` `*` `?` | one or more, zero or more, optional |
| `[abc]` | any one of these |
| `^` `$` | start and end |
| `( )` | a capture group |

```matlab
regexprep(strtrim(s), '\s+', ' ')     % collapse runs of whitespace
```

`strtrim` first: `\s+ -> ' '` would otherwise turn the leading whitespace into
a single leading space rather than removing it.

Reach for `strrep` when the thing you are replacing is literal text. A regular
expression that only ever matches one fixed string is harder to read and
slower, and it will surprise you the day the text contains a `.` or a `(`.

## char against string

Everything here works on char arrays. With a `string` you also get `strlength`,
`split`, `join` and `replace` as methods, and `+` concatenates. Remember this
course's engine has no string literal, so a string is made explicitly with
`string('...')`.

## Your turn

- `normalise_name(s)` — trimmed, lower case, internal whitespace collapsed
- `extract_numbers(s)` — every number in the text, as a numeric array
- `initials(fullname)` — `'ada lovelace'` to `'A.L'`; `''` for blank input
