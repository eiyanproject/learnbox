---
title: SQL injection
summary: The most famous web flaw - building a query by gluing strings together - broken with a crafted login, then closed with parameters.
order: 2
files: [injection.py]
run: python injection.py
hints:
  - "`injection_payload`: return a `(username, password)` where the username ends the string literal and comments out the rest of the query. In SQLite, `--` starts a comment."
  - "A username of `admin' --` turns `... WHERE username='admin' --' AND password='...'` into a query that finds admin and ignores the password entirely."
  - "`safe_login`: pass the values as parameters with `cur.execute(sql, (user, pw))` and `?` placeholders. The database then treats them as data, never as query text."
  - "The fix is not escaping quotes by hand - it is never letting user input become part of the query string in the first place."
---

A login checks a username and password against a database. The natural-looking
way to write that query is also the single most exploited bug in the history of
the web:

```python
cur.execute("SELECT username FROM users "
            "WHERE username='" + user + "' AND password='" + pw + "'")
```

The user's input is **glued directly into the query text**. The database cannot
tell where your query ends and the attacker's input begins, because by the time
it sees the string, there is no boundary left.

## The attack

Supply a username of `admin' --` and the query becomes:

```sql
SELECT username FROM users WHERE username='admin' --' AND password='...'
```

The `'` closes the username string early, and `--` turns the rest of the line -
the entire password check - into a comment. The database happily returns the
admin row, no password required. Variations (`' OR '1'='1`) dump every row; more
elaborate ones read other tables or the database version. You will write the
login-bypass payload yourself.

## The defence

The fix is **parameterised queries** (prepared statements). The query text and
the data travel separately, and the database treats the parameters as pure data
that can never change the query's structure:

```python
cur.execute("SELECT username FROM users WHERE username=? AND password=?",
            (user, pw))
```

Now `admin' --` is looked up as a literal username - no such user exists, and
the login fails as it should. The crucial mental shift: the bug is not "unescaped
quotes", it is **mixing code and data**. Escaping quotes by hand is the fragile
non-fix people reach for; parameters remove the mixing entirely. This same
principle - keep untrusted data out of the command - returns in every injection
flaw in the track.

## Your turn

`make_db()` is provided, with users `admin`/`s3cret` and `alice`/`password1`,
along with the vulnerable `login`. In `injection.py`:

- `injection_payload()` - return `(username, password)` that logs in as `admin`
  through the vulnerable `login` without knowing the password
- `safe_login(db, user, pw)` - the parameterised version: returns the username
  on success, `None` otherwise, and is immune to the payload
