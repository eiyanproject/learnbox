---
title: "Capstone: fixing a vulnerable app"
summary: One small application with three of the holes you have met. Close every one without breaking what the app is for.
order: 7
files: [app.py]
run: python app.py
hints:
  - "`login`: switch the concatenated query to a parameterised one with `?` placeholders. Correct credentials must still work."
  - "`render_message`: escape the text with `html.escape` so a script payload is shown, not run."
  - "`read_note`: return the note only when its owner matches the requesting user, else `None`."
  - "Each fix is exactly the one from its lesson; the capstone is making all three live together in one working app."
---

Real code does not come one flaw at a time. Here is a small message board with
three holes you now recognise, and your job is the real one: close every hole
while the application keeps doing what it is for. A fix that also breaks login is
not a fix.

The `App` class in `app.py` has three vulnerable methods:

- **`login`** builds its SQL by concatenation - open to the injection from the
  SQL lesson.
- **`render_message`** drops user text straight into HTML - stored XSS.
- **`read_note`** returns any note by id without checking the owner - an IDOR.

Fix all three **in place**, keeping the method signatures and the legitimate
behaviour: real users log in, real messages display, owners read their notes.

This is the shape of actual security work - not finding one bug in isolation,
but hardening a working system against several classes of attack at once, and
knowing you have not broken it because the tests for normal use still pass
alongside the tests that the attacks now fail.

## Your turn

In `app.py`, fix `login`, `render_message` and `read_note`. Keep what each
returns: `login` gives the username or `None`; `render_message` gives
`<li class='msg'>...</li>` with the text inside escaped; `read_note` gives the
note's text only when `user` owns it, and `None` otherwise - including for an id
that does not exist. The checks confirm each attack is closed **and** that
ordinary use still works.
