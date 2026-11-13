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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **char array** | text as a row of characters: `'abc'` |
| **string** | MATLAB's text type; made here with `string('...')` |
| **whitespace** | spaces, tabs and newlines |
| **literal replacement** | replacing exact text, no patterns |
| **element by element** | `==` on char arrays compares each position |
| **regular expression** | a pattern that matches text |
| **capture group** | `( )`: a part of the match kept separately |
| **token** | the text a capture group matched |
| **cell array** | `{ }`: a container that can hold text of different lengths |
| **collapse** | turn runs of spaces into one |
| **initials** | first letters, such as `'A.L'` |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `octave --no-gui --quiet --eval "..."` | runs one line of MATLAB code in Octave, with no window and no banner, as Run does |

### MATLAB names

| Name | What it does |
|---|---|
| `strtrim(s)` | drops leading and trailing whitespace |
| `lower(s)`, `upper(s)` | changes case |
| `strrep(s, a, b)` | replaces literal text |
| `strsplit(s)`, `strjoin(c, sep)` | splits text / joins pieces |
| `strcmp`, `strcmpi` | compare exactly / ignoring case |
| `contains`, `startsWith`, `endsWith` | membership tests |
| `sprintf(fmt, ...)` | builds formatted text |
| `regexp(s, p, 'match')`, `'once'`, `'tokens'` | all matches / the first / capture groups |
| `regexprep(s, p, repl)` | replaces matches |
| `\d`, `\s`, `\w`, `+`, `*`, `?`, `[abc]`, `^`, `$` | digit, whitespace, word character, repeats, a set, start, end |
| `m{:}`, `t{1}{2}` | the contents of a cell array |
| `str2double` | text to a number |
| `strlength`, `split`, `join`, `replace` | the string versions |

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

## Run

```matlab
disp('abc' == 'abd')
disp(strcmp('abc', 'abd'))
try
  tf = 'abc' == 'abcd';
catch
  disp('different lengths: an error')
end
disp(regexprep(strtrim('  too   many  spaces '), '\s+', ' '))
m = regexp('a1 b22 c333', '\d+', 'match');
fprintf('%s ', m{:}); fprintf('\n');
disp(regexp('a1 b22', '\d+', 'match', 'once'))
t = regexp('key=value', '(\w+)=(\w+)', 'tokens');
fprintf('%s %s\n', t{1}{1}, t{1}{2});
disp(strrep('a.b.c', '.', '-'))
```

```output
1 1 0
0
different lengths: an error
too many spaces
1 22 333
1
key value
a-b-c
```

## Your turn

- `normalise_name(s)` — trimmed, lower case, internal whitespace collapsed
- `extract_numbers(s)` — every number in the text, as a numeric array
- `initials(fullname)` — `'ada lovelace'` to `'A.L'`; `''` for blank input
