---
title: Build a mini ORM
summary: Combine descriptors, __init_subclass__ and sqlite3 into a tiny object-relational mapper.
order: 7
files: [orm.py]
run: python -i orm.py
hints:
  - "`Field.__set_name__` records `self.name`. `Model.__init_subclass__` collects `cls._fields = {name: f for name, f in vars(cls).items() if isinstance(f, Field)}` and sets `cls._table = cls.__name__.lower() + \"s\"`."
  - "`create_table(conn)`: `columns = \", \".join(f\"{n} {f.sql_type}\" for n, f in cls._fields.items())` and execute `CREATE TABLE IF NOT EXISTS {table} (id INTEGER PRIMARY KEY AUTOINCREMENT, {columns})`."
  - "`save(conn)`: if `self.id` is None run an INSERT with `?` placeholders and set `self.id = cursor.lastrowid`; otherwise run an UPDATE. Never format values into the SQL string."
  - "`find(conn, **filters)`: build `WHERE a = ? AND b = ?` from the keyword names (checked against `_fields`), pass the values as parameters, and turn each row back into an instance with `cls(**dict(zip(names, row)))`."
---

Programs think in objects; databases think in tables of rows and columns.
Moving data between the two by hand means writing the same SQL again and
again for every class: an `INSERT` to save one, a `SELECT` to load it, code to
turn each row back into an object. An **ORM** (object-relational mapper) does
that translation for you: it maps classes to database tables and objects to
rows. Real ones (SQLAlchemy, Django's) are large, but the core is small, and
building one uses nearly every advanced Python feature from this course. By
the end of this lesson, this works:

```python
class User(Model):
    name = Text()
    age = Integer()

User.create_table(conn)
u = User(name="Ana", age=31)
u.save(conn)                       # INSERT, sets u.id
User.find(conn, name="Ana")        # [User(id=1, name='Ana', age=31)]
```

(The goal, not yet runnable: `Model`, `Text` and `Integer` are what you
build in the exercise.)

The class body is a **declaration**: two lines say what columns a user has,
and the ORM works out the table, the SQL and the conversion from that.

## sqlite3 in two minutes

**SQL** is the standard language for talking to relational databases.
**SQLite** is a full SQL database stored in one file, with no server to run,
and the `sqlite3` module that talks to it ships with Python:

```pycon
>>> import sqlite3
>>> conn = sqlite3.connect(":memory:")          # or a file path
>>> conn.execute("CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT)")
<sqlite3.Cursor object at 0x...>
>>> cur = conn.execute("INSERT INTO notes (body) VALUES (?)", ("hello",))
>>> cur.lastrowid                                # the new id
1
>>> conn.execute("SELECT id, body FROM notes WHERE body = ?", ("hello",)).fetchall()
[(1, 'hello')]
>>> conn.commit()
```

Line by line:

- `sqlite3.connect(path)` opens a database file, creating it if needed.
  `":memory:"` is a special name for a temporary database in memory, which
  vanishes when the connection closes; ideal for tests.
- `CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT)` makes a table with
  two columns. `INTEGER PRIMARY KEY` means each row gets a unique number,
  filled in automatically.
- `conn.execute(sql, params)` runs one SQL statement and returns a **cursor**,
  an object for reading the results.
- `INSERT INTO notes (body) VALUES (?)` adds a row. The `?` is a
  **placeholder**: the value comes from the tuple `("hello",)`, passed
  separately. `cur.lastrowid` is the id the database gave the new row.
- `SELECT id, body FROM notes WHERE body = ?` reads rows back, and
  `fetchall()` returns them as a list of tuples, one tuple per row, with the
  columns in the order you asked for.
- `conn.commit()` makes the changes permanent. Until then they belong to an
  open transaction and are lost if the program stops.

**Always pass values as parameters (`?`), never with f-strings.** Formatting
user input into SQL is **SQL injection**: if a user types the "name"
`x'); DROP TABLE users; --`, an f-string pastes that text into your SQL,
where the database runs it as commands. With a `?`, the value is sent
separately and is only ever treated as data, whatever characters it
contains. One of this lesson's tests saves exactly that name.

Identifiers (table and column names) cannot be parameters: `?` only works
for values. So the ORM must build those parts of the SQL from names it
defined itself, the fields declared in the class, and must reject any others
it is handed, for example as filter keywords.

## The pieces

**Descriptors** (from the Advanced section) describe each column and
validate values. Each field is a descriptor on the class, knows its own name
through `__set_name__`, and knows its SQL type:

```python
class Field:
    sql_type = "TEXT"
    def __set_name__(self, owner, name): self.name = name
    def __get__(self, obj, objtype=None): ...
    def __set__(self, obj, value): ...
```

(A skeleton: the bodies marked `...` are for you to write.)

**`__init_subclass__`** (Pro: Metaprogramming) runs when `class User(Model)`
is defined, and is the moment to collect the fields and decide the table
name. `vars(cls)` is the class's own namespace, a dict in definition order,
so picking out the values that are `Field`s gives you the columns, in the
order they were written:

```pycon
>>> class Field:
...     pass
...
>>> class Example:
...     name = Field()
...     age = Field()
...     def greet(self): ...
...
>>> [n for n, v in vars(Example).items() if isinstance(v, Field)]
['name', 'age']
```

**Class methods** act on the table as a whole (`create_table`, `get`,
`find`), so they receive the class as `cls`; **instance methods** act on one
row (`save`, `delete`), so they receive the object as `self`.

The SQL statements are then built from those collected names. For `User`,
the ORM would produce:

```sql
CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, age INTEGER)
INSERT INTO users (name, age) VALUES (?, ?)
UPDATE users SET name = ?, age = ? WHERE id = ?
SELECT id, name, age FROM users WHERE age = ? ORDER BY id
```

Only the names come from the class; every value is a `?`. `IF NOT EXISTS`
makes creating the table safe to repeat, and `AUTOINCREMENT` stops ids of
deleted rows from being reused.

## Mapping rows back to objects

A query returns tuples, such as `(1, 'Ana', 31)`. If the query always lists
the columns in a known order, `id` and then the fields in definition order,
pairing those names with the tuple gives keyword arguments for the class:

```pycon
>>> names = ["id", "name", "age"]
>>> row = (1, "Ana", 31)
>>> dict(zip(names, row))
{'id': 1, 'name': 'Ana', 'age': 31}
```

`cls(**dict(zip(names, row)))` then builds the object, passing each column as
a keyword argument, the unpacking from Functions in depth.

## What real ORMs add

Relationships between tables (a user *has many* orders) and the joins to
load them, lazy loading (fetching related rows only when they are first
used), a unit of work that batches many changes into a few writes,
migrations (changing the tables as the classes change, without losing data),
and a query builder for conditions more complex than "equals". It is all
built on the same ideas you use here.

## Your turn

In `orm.py`:

- `Field`, with `__set_name__`, `__get__` (the descriptor itself when read on
  the class; on an instance, the value, or `None` if it was never set) and
  `__set__` calling `validate` before storing. `Integer` (`sql_type =
  "INTEGER"`, an `int` but not a `bool`) and `Text` (`sql_type = "TEXT"`, a
  `str`) raise `TypeError` for wrong types. `None` is always allowed.
- `Model`:
  - each subclass collects its fields, in definition order, into
    `cls._fields` (a dict from name to `Field`), and sets `cls._table` to the
    class name lower-cased plus `s` (`User` gives `users`);
  - `__init__(**kwargs)` accepts `id` and the field names only; any other
    keyword raises `TypeError`. Fields not given are `None`, and so is `id`
    for a new object;
  - `__repr__` like `User(id=1, name='Ana', age=31)`: `id` first, then every
    field in order, values shown with `repr`;
  - `create_table(conn)`: a table with an `id` column followed by one column
    per field, with the field's SQL type;
  - `save(conn)`: insert a new row if `id` is `None` (and set `id` to the new
    row's id), otherwise update the existing row. It returns the object
    itself, so `User(...).save(conn)` gives you the saved user;
  - `delete(conn)`: delete the row and set `id` back to `None`;
  - `get(conn, id)`: the instance with that id, or `None`;
  - `find(conn, **filters)`: a list of instances whose fields equal all the
    given values, ordered by id; no filters returns every row. An unknown
    filter name raises `ValueError` (it must never reach the SQL);
  - every value goes through a `?` parameter.
- Each model has its own table, and they do not interfere: `Book` and `User`
  ids both start at 1.
