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

## Your turn

- `validate_scores(v)` — returns `true`, or throws `validate_scores:empty`,
  `validate_scores:notNumeric` or `validate_scores:outOfRange`
- `try_parse(text)` — returns `[ok, value]`; a failure is not an error
- `error_id_of(f)` — the identifier `f` throws, or `''` when it throws nothing
