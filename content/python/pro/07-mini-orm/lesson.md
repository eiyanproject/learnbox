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

An **ORM** maps classes to database tables and objects to rows. Real ones
(SQLAlchemy, Django) are large, but the core is small, and building one uses
nearly every advanced Python feature from this track.

```python
class User(Model):
    name = Text()
    age = Integer()

User.create_table(conn)
u = User(name="Ana", age=31)
u.save(conn)                       # INSERT, sets u.id
User.find(conn, name="Ana")        # [User(id=1, name='Ana', age=31)]
```

## sqlite3 in two minutes

SQLite is a full SQL database in one file, and it ships with Python:

```python
import sqlite3

conn = sqlite3.connect(":memory:")          # or a file path
conn.execute("CREATE TABLE notes (id INTEGER PRIMARY KEY, body TEXT)")
cur = conn.execute("INSERT INTO notes (body) VALUES (?)", ("hello",))
cur.lastrowid                                # the new id
rows = conn.execute("SELECT id, body FROM notes WHERE body = ?", ("hello",)).fetchall()
conn.commit()
```

**Always pass values as parameters (`?`), never with f-strings.** Formatting user
input into SQL is SQL injection. Identifiers (table and column names) cannot be
parameters, so the ORM must only ever use names it defined itself, and must
reject any others.

## The pieces

**Descriptors** (Advanced track) describe each column and validate values:

```python
class Field:
    sql_type = "TEXT"
    def __set_name__(self, owner, name): self.name = name
    def __get__(self, obj, objtype=None): ...
    def __set__(self, obj, value): ...
```

**`__init_subclass__`** (Pro: Metaprogramming) runs when `class User(Model)` is
defined, and is the moment to collect the fields and decide the table name.

**Class methods** act on the table (`create_table`, `find`); **instance methods**
act on one row (`save`, `delete`).

## Mapping rows back to objects

A query returns tuples. Knowing the column order (`id` then the fields, in
definition order) turns each into keyword arguments for the class.

## What real ORMs add

Relationships and joins, lazy loading, a unit-of-work that batches writes,
migrations, and a query builder. It is all built on the same ideas.

## Your turn

In `orm.py`:

- `Field` with `__set_name__`, `__get__` (the descriptor on the class, the value
  or `None` on instances) and `__set__` calling `validate`; `Integer` (int, not
  bool, `sql_type = "INTEGER"`) and `Text` (str, `sql_type = "TEXT"`) raise
  `TypeError` for wrong types. `None` is always allowed.
- `Model`:
  - subclasses collect their fields in order; the table name is the class name lower-cased plus `s`
  - `__init__(**kwargs)` accepts `id` and field names only (others: `TypeError`)
  - `__repr__` like `User(id=1, name='Ana', age=31)`
  - `create_table(conn)`, `save(conn)` (insert or update), `delete(conn)`,
    `get(conn, id)` (instance or `None`), `find(conn, **filters)` (list ordered
    by id; unknown filter names raise `ValueError`)
  - all values go through `?` parameters
