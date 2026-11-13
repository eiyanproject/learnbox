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

## Chapter 0: the words in this lesson

Every term, command and function this lesson uses, with what it means. Read
it first, or come back whenever a word is unfamiliar; each one is explained
again, with examples, where the lesson uses it.

### Terms

| Term | Meaning |
|---|---|
| **database** | a program that stores data in tables and answers questions about it |
| **table**, **row**, **column** | a grid of data; one record; one field of every record |
| **SQL** | the language for asking a database questions |
| **query** | one SQL statement, such as `SELECT ... FROM ... WHERE ...` |
| **`SELECT ... FROM ... WHERE ...`** | "give me these columns, from this table, for the rows where this is true" |
| **string literal** | text inside quotes in SQL: `'admin'` |
| **comment** | text the database ignores; in SQLite (and most SQL) `--` starts one, to the end of the line |
| **concatenation** | building a string by gluing pieces together with `+` |
| **SQL injection** | input that changes the structure of a query, because it was glued into the query text |
| **payload** | the crafted input that carries an attack |
| **login bypass** | getting logged in without the right password |
| **parameterised query** (prepared statement) | a query with placeholders, whose values are sent separately and only ever treated as data |
| **placeholder** | the `?` in a parameterised query, where a value goes |
| **escaping** | putting a backslash or a second quote before special characters; fragile, and not the fix |
| **allow-list** | the only values accepted, everything else refused; for things that cannot be parameters, such as a column name |
| **least privilege** | the application's database account may do only what it needs |
| **mixing code and data** | the root cause of every injection flaw |
| **SQLite** | a small database inside one file (or, here, in memory), built into Python |

### Commands (typed in the terminal)

| Command | What it does |
|---|---|
| `python injection.py` | runs your program: tries the payload on the vulnerable and the safe login |

### Python names

| Name | What it does |
|---|---|
| `import sqlite3` | loads Python's SQLite module |
| `sqlite3.connect(":memory:")` | a new, empty database that lives only in memory |
| `db.execute(sql)` | runs one SQL statement |
| `db.execute(sql, (user, pw))` | runs it with `user` and `pw` sent as the values of the `?` placeholders |
| `.fetchone()` | the first row of the result, as a tuple, or `None` if there is none |
| `row[0]` | the first column of that row |
| `x if row else None` | `x` when there is a row, otherwise `None` |
| `return ("admin' --", "anything")` | returns a pair of values, a tuple |
| `make_db()` | given to you: the database with two users |
| `login(db, user, pw)` | given to you: the **vulnerable** login |

---

A login checks a username and password against a database. The
natural-looking way to write that check is also the most exploited bug in the
history of the web:

```python
sql = ("SELECT username FROM users WHERE username='"
       + user + "' AND password='" + pw + "'")
```

Read the SQL as "give me the `username` column from the `users` table, for the
row whose username is this and whose password is that". If a row comes back,
the login succeeds.

The problem is how the query is built: the user's input is **glued directly
into the query text**. By the time the database receives the string, it
cannot tell which parts you wrote and which parts the user typed. There is no
boundary left.

## The attack

SQL marks text with single quotes (`'admin'`) and treats everything from `--`
to the end of the line as a **comment**, which it ignores. Now type this as
the username:

```text
admin' --
```

and the query becomes:

```sql
SELECT username FROM users WHERE username='admin' --' AND password='...'
```

1. The `'` closes the username's text early, right after `admin`.
2. The `--` makes everything after it a comment, including the whole password
   check.
3. What the database actually runs is
   `SELECT username FROM users WHERE username='admin'`.

It returns the admin row, and the login succeeds without any password. The
user's input changed the **structure** of the query, not just a value in it.
That is **SQL injection**. Other inputs can make the condition always true or
read other tables entirely. You will write the login-bypass payload yourself,
against the in-memory database the lesson gives you.

## The defence: parameters

The fix is a **parameterised query** (also called a prepared statement). The
query text has `?` **placeholders**, and the values travel separately:

```python
db.execute("SELECT username FROM users WHERE username=? AND password=?",
           (user, pw))
```

The database reads the query's structure first, and only then fills in the
values, as **data**. Nothing in a value can ever become part of the query.
Now `admin' --` is looked up as a username, quote, dashes and all. There is no
user with that name, so the login fails, as it should.

```text
vulnerable login as: admin
safe login with payload: None
safe login, real creds: admin
```

The important shift in thinking: the bug is not "the quotes were not escaped".
It is **mixing code and data**. Escaping quotes by hand is the fragile non-fix
people reach for, and OWASP's SQL Injection Prevention Cheat Sheet strongly
discourages it. Parameters remove the mixing completely.

Two extra layers, from the same cheat sheet:

- Some parts of a query cannot be parameters, such as a column name chosen for
  sorting. For those, accept only values from an **allow-list**
  (`"name"`, `"date"`) and refuse everything else.
- Give the application's database account **least privilege**: a login page
  needs to read the `users` table, not to drop it.

The same principle, keep untrusted data out of the command, comes back in
every injection flaw in this section.

## Your turn

`make_db()` is given to you, with the users `admin` (password `s3cret`) and
`alice` (password `password1`), and so is the vulnerable `login`. In
`injection.py`:

- `injection_payload()`: return a `(username, password)` pair that logs in as
  `admin` through the vulnerable `login` without knowing the password.
- `safe_login(db, user, pw)`: the parameterised version. It returns the
  username on success and `None` otherwise, and the payload does not work on
  it.

## Check yourself

1. What does `--` do in the attack?
   *It turns the rest of the query, the password check, into a comment.*
2. What does the `'` in `admin' --` do?
   *It closes the username's text early.*
3. Why does a parameterised query stop the attack?
   *The values are sent separately and only ever treated as data.*
4. Why is escaping quotes by hand not the real fix?
   *It is easy to get wrong; the real problem is mixing code and data.*
5. A user can choose the column to sort by. It cannot be a parameter. What
   then?
   *Check it against an allow-list of real column names.*
