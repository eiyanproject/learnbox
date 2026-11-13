---
title: Errors and debugging
summary: Throwing with an identifier, catching the one you meant, and the difference between a failure you expected and a bug.
order: 2
files: [validate_scores.m, try_parse.m, error_id_of.m]
run: octave --no-gui --quiet --eval "disp(error_id_of(@() validate_scores([1 2 300])))"
hints:
  - "`error('component:mnemonic', 'text %d', n)` - the identifier comes first and is the part code may depend on."
  - "Check in order and throw a DIFFERENT identifier for each failure, so a caller can tell them apart."
  - "`try ... catch err ... end` gives you `err.identifier` and `err.message`."
  - "`error_id_of` returns '' when nothing was thrown - which is a fact about the call, not a failure."
---

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **error identifier** | `component:mnemonic`: a stable name code can match |
| **error message** | text for a person; may change |
| **mnemonic** | a short memorable word, such as `outOfRange` |
| **`try` / `catch`** | run code, and handle an error if one is thrown |
| **`err`** | the error object: `err.identifier`, `err.message` |
| **rethrow** | pass the original error on, with its stack |
| **stack** | the chain of calls that led to the error |
| **swallow** | catch an error and do nothing, hiding it |
| **expected failure** | a normal outcome, such as bad user input: return a flag |
| **bug** | a caller's mistake: throw |
| **validation** | checking arguments before using them |
| **breakpoint** | a place where the debugger stops |
| **function handle** | `@() ...`: a function stored in a variable |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `octave --no-gui --quiet --eval "..."` | runs one line of MATLAB code in Octave, with no window and no banner, as Run does |

### MATLAB names

| Name | What it does |
|---|---|
| `error('id:name', 'message %g', x)` | throws an error with an identifier |
| `try ... catch err ... end` | catches it |
| `switch err.identifier ... case '...' ... end` | handles by identifier |
| `strcmp(a, b)` | whether two char arrays are equal |
| `rethrow(err)` | passes it on unchanged |
| `validateattributes(v, {'numeric'}, {'vector', 'nonempty'})` | checks type and shape |
| `assert(cond, 'id:name', 'message')` | throws if `cond` is false |
| `isnumeric(v)`, `isempty(v)` | type and emptiness tests |
| `dbstop if error` | stops in the debugger where an error happens |
| `keyboard` | a prompt at this line |
| `dbstack` | how you got here |
| `warning('off', id)` | silences one warning |
| `str2double(text)` | text to number; `NaN` if it is not one |

---

## Identifiers

```matlab
error('validate_scores:outOfRange', 'score %g is outside 0 to 100', s);
```

Two parts, and they are for different readers. The **identifier**
(`component:mnemonic`) is for code: `catch err` gives `err.identifier`, and it
is stable. The **message** is for a person and may be reworded at any time.

Matching on the message is the mistake this exists to prevent.

```matlab
try
  risky();
catch err
  switch err.identifier
    case 'validate_scores:outOfRange'
      ...
  end
end
```

## Catch what you can handle

```matlab
catch err
  if ~strcmp(err.identifier, 'parse:bad')
    rethrow(err);          % not mine - let it travel
  end
  ...
end
```

A bare `catch` that swallows everything turns a crash into wrong output, which
is worse. `rethrow(err)` passes on the original with its stack intact;
`error(...)` inside a catch starts a new one and loses it.

## Expected failure against a bug

The same question as everywhere: **is this a normal outcome of correct code?**

User typed letters into a number box — normal. Return a flag, use the `Try`
pattern, hand back a status. A negative length, a null where one is required,
an index off the end — those mean the caller has a bug. Throw.

## Validating

```matlab
validateattributes(v, {'numeric'}, {'vector', 'nonempty'});
assert(all(v >= 0), 'scores:negative', 'scores must not be negative');
```

`validateattributes` produces a standard message naming the argument.
`assert` with an identifier is the compact form. Both throw — they are for
programming errors, not user input.

## Debugging

| | |
|---|---|
| `dbstop if error` | break at the point of failure, with the workspace intact |
| `keyboard` | drop into a prompt at a chosen line |
| `dbstack` | how you got here |
| `warning('off', id)` | silence one warning, never all of them |

`dbstop if error` is the one worth remembering. The alternative — adding
`disp` calls and re-running — loses the state that caused the problem.

## Run

```matlab
try
  error('validate_scores:outOfRange', 'score %g is outside 0 to 100', 120);
catch err
  fprintf('%s\n%s\n', err.identifier, err.message);
end

try
  try
    error('parse:other', 'not the one we handle');
  catch err
    if ~strcmp(err.identifier, 'parse:bad')
      rethrow(err);              % not ours: let it travel
    end
  end
catch outer
  disp(outer.identifier)
end
```

```output
validate_scores:outOfRange
score 120 is outside 0 to 100
parse:other
```

## Your turn

- `validate_scores(v)` — returns `true`, or throws `validate_scores:empty`,
  `validate_scores:notNumeric` or `validate_scores:outOfRange`
- `try_parse(text)` — returns `[ok, value]`; a failure is not an error
- `error_id_of(f)` — the identifier `f` throws, or `''` when it throws nothing
