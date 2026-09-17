import sqlite3


class Field:
    sql_type = "TEXT"

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__.get(self.name)

    def __set__(self, obj, value):
        if value is not None:
            self.validate(value)
        obj.__dict__[self.name] = value

    def validate(self, value):
        pass


class Integer(Field):
    sql_type = "INTEGER"

    def validate(self, value):
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{self.name} must be an int")


class Text(Field):
    sql_type = "TEXT"

    def validate(self, value):
        if not isinstance(value, str):
            raise TypeError(f"{self.name} must be a str")


class Model:
    _fields = {}
    _table = ""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._fields = {name: f for name, f in vars(cls).items() if isinstance(f, Field)}
        cls._table = cls.__name__.lower() + "s"

    def __init__(self, **kwargs):
        self.id = kwargs.pop("id", None)
        unknown = set(kwargs) - set(self._fields)
        if unknown:
            raise TypeError(f"unknown fields: {', '.join(sorted(unknown))}")
        for name in self._fields:
            setattr(self, name, kwargs.get(name))

    def __repr__(self):
        parts = [f"id={self.id!r}"] + [f"{n}={getattr(self, n)!r}" for n in self._fields]
        return f"{type(self).__name__}({', '.join(parts)})"

    @classmethod
    def create_table(cls, conn):
        columns = ", ".join(f"{n} {f.sql_type}" for n, f in cls._fields.items())
        conn.execute(f"CREATE TABLE IF NOT EXISTS {cls._table} (id INTEGER PRIMARY KEY AUTOINCREMENT, {columns})")
        conn.commit()

    def save(self, conn):
        names = list(self._fields)
        values = [getattr(self, n) for n in names]
        if self.id is None:
            placeholders = ", ".join("?" for _ in names)
            cur = conn.execute(f"INSERT INTO {self._table} ({', '.join(names)}) VALUES ({placeholders})", values)
            self.id = cur.lastrowid
        else:
            assignments = ", ".join(f"{n} = ?" for n in names)
            conn.execute(f"UPDATE {self._table} SET {assignments} WHERE id = ?", values + [self.id])
        conn.commit()
        return self

    def delete(self, conn):
        if self.id is not None:
            conn.execute(f"DELETE FROM {self._table} WHERE id = ?", (self.id,))
            conn.commit()
            self.id = None

    @classmethod
    def _rows_to_objects(cls, rows):
        names = ["id"] + list(cls._fields)
        return [cls(**dict(zip(names, row))) for row in rows]

    @classmethod
    def find(cls, conn, **filters):
        unknown = set(filters) - set(cls._fields) - {"id"}
        if unknown:
            raise ValueError(f"unknown filter fields: {', '.join(sorted(unknown))}")
        columns = ", ".join(["id"] + list(cls._fields))
        sql = f"SELECT {columns} FROM {cls._table}"
        if filters:
            sql += " WHERE " + " AND ".join(f"{name} = ?" for name in filters)
        sql += " ORDER BY id"
        return cls._rows_to_objects(conn.execute(sql, list(filters.values())).fetchall())

    @classmethod
    def get(cls, conn, id):
        found = cls.find(conn, id=id)
        return found[0] if found else None
