import sqlite3


class Field:
    sql_type = "TEXT"


class Integer(Field):
    sql_type = "INTEGER"


class Text(Field):
    sql_type = "TEXT"


class Model:
    pass


# Try it:
# class User(Model):
#     name = Text()
#     age = Integer()
#
# conn = sqlite3.connect(":memory:")
# User.create_table(conn)
# User(name="Ana", age=31).save(conn)
# print(User.find(conn, name="Ana"))
