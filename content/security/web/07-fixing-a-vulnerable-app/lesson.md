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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **capstone** | a final exercise that combines everything in a section |
| **vulnerability** (hole) | a flaw an attacker can use |
| **SQL injection** | input glued into a query changes the query (Web lesson 2) |
| **stored XSS** | saved user text put into a page unescaped, so it runs as script (Web lesson 3) |
| **IDOR** | returning any object by ID without checking its owner (Web lesson 4) |
| **fix in place** | change the body of a method without changing its name, arguments or what it returns |
| **regression** | a change that breaks something that used to work |
| **legitimate behaviour** | what the app is for: real users log in, real messages show, owners read their notes |
| **hardening** | closing holes in a working system |
| **parameterised query** | a query with `?` placeholders, values sent separately |
| **escape on output** | turn `<`, `>`, `&` and quotes into entities before they go into HTML |
| **ownership check** | return a resource only to the user it belongs to |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python app.py` | runs the app's three methods once: a login, a message render, a note read |

### Python names

| Name | What it does |
|---|---|
| `class App:` | defines the app as a class; its methods are the functions inside it |
| `self` | the app object itself, passed to every method |
| `self.db` | the app's in-memory SQLite database |
| `self.notes` | the app's notes, a dict of `{id: {"owner": ..., "text": ...}}` |
| `self.db.execute(sql, (user, pw))` | runs a parameterised query |
| `.fetchone()` | the first row, or `None` |
| `html.escape(text)` | `text` made safe to place in HTML |
| `self.notes.get(note_id)` | the note, or `None` for an ID that does not exist |
| `<li class='msg'>...</li>` | one item of an HTML list: how each message is shown |

---

Real code does not come with one flaw at a time. Here is a small message
board with three holes you now recognise. Your job is the real one: close
every hole while the application keeps doing what it is for. A fix that also
breaks logging in is not a fix.

## The three holes

The `App` class in `app.py` has three vulnerable methods:

| Method | What is wrong | Lesson | The fix |
|---|---|---|---|
| `login` | builds its SQL by gluing strings together | SQL injection | a parameterised query with `?` placeholders |
| `render_message` | puts user text straight into HTML | cross-site scripting | `html.escape` the text |
| `read_note` | returns any note by ID, whoever asks | broken access control | return it only to its owner |

Running the unfixed app shows two of them at once: the script tag comes out
live, and `alice` reads the admin's note.

```text
login admin: admin
render: <li class='msg'><script>evil()</script></li>
alice reads note 1: launch codes
```

## Fix without breaking

Fix all three **in place**. Keep each method's name, its arguments and what
it returns, and keep the **legitimate behaviour**:

- real users still log in with their real passwords;
- ordinary messages still display, with characters such as `&` shown
  correctly;
- owners can still read their own notes.

This is what security work actually looks like. You are not finding one bug
on its own, but **hardening** a working system against several kinds of
attack at once. You know you have not broken it because the tests for
normal use still pass, alongside the tests that check each attack now
fails. A change that closes a hole but breaks normal use is a
**regression**, and in a real team it would be reverted.

When it is done, the same run shows the script as harmless text and the
note withheld:

```text
login admin: admin
render: <li class='msg'>&lt;script&gt;evil()&lt;/script&gt;</li>
alice reads note 1: None
```

## Your turn

In `app.py`, fix `login`, `render_message` and `read_note`. Keep what each
returns:

- `login(user, pw)` gives the username, or `None`.
- `render_message(text)` gives `<li class='msg'>...</li>` with the text
  inside escaped.
- `read_note(note_id, user)` gives the note's text only when `user` owns it,
  and `None` otherwise, including for an ID that does not exist.

The checks confirm that each attack is closed **and** that ordinary use still
works.

## Check yourself

1. Which of the three fixes stops `admin' --` from logging in?
   *The parameterised query in `login`.*
2. After your fix, what should `render_message("Tom & Jerry")` show?
   *`<li class='msg'>Tom &amp; Jerry</li>`: still readable.*
3. What should `read_note(99, "alice")` return?
   *`None`: the note does not exist.*
4. Why do the checks test normal use as well as the attacks?
   *A fix that breaks normal use is a regression, not a fix.*
5. What one idea lies behind all three fixes?
   *Treat untrusted input as data, and check who may do what, on the
   server.*
