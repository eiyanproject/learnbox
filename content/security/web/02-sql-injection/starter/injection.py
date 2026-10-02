import sqlite3


def make_db():
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE users (username TEXT, password TEXT)")
    db.execute("INSERT INTO users VALUES ('admin', 's3cret')")
    db.execute("INSERT INTO users VALUES ('alice', 'password1')")
    return db


def login(db, user, pw):
    # VULNERABLE: user input is concatenated straight into the query.
    sql = ("SELECT username FROM users WHERE username='"
           + user + "' AND password='" + pw + "'")
    row = db.execute(sql).fetchone()
    return row[0] if row else None


def injection_payload():
    # Return (username, password) that logs in as admin via `login` above.
    pass


def safe_login(db, user, pw):
    # The parameterised version, immune to the payload.
    pass


if __name__ == "__main__":
    db = make_db()
    u, p = injection_payload()
    print("vulnerable login as:", login(db, u, p))
    print("safe login with payload:", safe_login(db, u, p))
    print("safe login, real creds:", safe_login(db, "admin", "s3cret"))
