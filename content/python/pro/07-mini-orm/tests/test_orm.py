import sqlite3

import pytest

from orm import Field, Integer, Model, Text


class User(Model):
    name = Text()
    age = Integer()


class Book(Model):
    title = Text()
    pages = Integer()
    author = Text()


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    User.create_table(c)
    Book.create_table(c)
    yield c
    c.close()


def test_fields_collected_in_order():
    assert list(User._fields) == ["name", "age"]
    assert list(Book._fields) == ["title", "pages", "author"]
    assert User._table == "users" and Book._table == "books"
    assert isinstance(User.__dict__["age"], Field)


def test_create_table_columns(conn):
    cols = [row[1] for row in conn.execute("PRAGMA table_info(users)")]
    assert cols == ["id", "name", "age"]


def test_validation():
    with pytest.raises(TypeError):
        User(name=5)
    with pytest.raises(TypeError):
        User(age="old")
    with pytest.raises(TypeError):
        User(age=True)
    with pytest.raises(TypeError):
        User(email="x@y")
    assert User(name=None).name is None


def test_repr():
    assert repr(User(name="Ana", age=31)) == "User(id=None, name='Ana', age=31)"


def test_insert_sets_id_and_get(conn):
    u = User(name="Ana", age=31).save(conn)
    assert u.id == 1
    loaded = User.get(conn, 1)
    assert repr(loaded) == "User(id=1, name='Ana', age=31)"
    assert User.get(conn, 99) is None


def test_update(conn):
    u = User(name="Ana", age=31).save(conn)
    u.age = 32
    u.save(conn)
    assert User.get(conn, u.id).age == 32
    assert conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 1


def test_find_filters_and_order(conn):
    for name, age in [("Budi", 30), ("Ana", 30), ("Citra", 45)]:
        User(name=name, age=age).save(conn)
    assert [u.name for u in User.find(conn, age=30)] == ["Budi", "Ana"]
    assert [u.name for u in User.find(conn, age=30, name="Ana")] == ["Ana"]
    assert len(User.find(conn)) == 3


def test_find_rejects_unknown_fields(conn):
    with pytest.raises(ValueError):
        User.find(conn, **{"age; DROP TABLE users": 1})


def test_values_are_parameters_not_sql(conn):
    evil = "x'); DROP TABLE users; --"
    User(name=evil, age=1).save(conn)
    assert User.find(conn, name=evil)[0].name == evil
    assert conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 1


def test_delete(conn):
    u = User(name="Ana", age=1).save(conn)
    u.delete(conn)
    assert u.id is None
    assert User.find(conn) == []


def test_models_are_independent(conn):
    Book(title="Dune", pages=412, author="Herbert").save(conn)
    User(name="Ana", age=31).save(conn)
    assert Book.get(conn, 1).title == "Dune"
    assert User.get(conn, 1).name == "Ana"
