import sqlite3
import html


class App:
    def __init__(self):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("CREATE TABLE users (username TEXT, password TEXT)")
        self.db.execute("INSERT INTO users VALUES ('admin', 's3cret')")
        self.db.execute("INSERT INTO users VALUES ('alice', 'password1')")
        self.notes = {
            1: {"owner": "admin", "text": "launch codes"},
            2: {"owner": "alice", "text": "shopping list"},
        }

    def login(self, user, pw):
        # VULNERABLE: fix the injection, keep real logins working.
        sql = ("SELECT username FROM users WHERE username='"
               + user + "' AND password='" + pw + "'")
        row = self.db.execute(sql).fetchone()
        return row[0] if row else None

    def render_message(self, text):
        # VULNERABLE: fix the XSS, keep ordinary messages readable.
        return f"<li class='msg'>{text}</li>"

    def read_note(self, note_id, user):
        # VULNERABLE: fix the IDOR, keep owners able to read their own notes.
        note = self.notes.get(note_id)
        return note["text"] if note else None


if __name__ == "__main__":
    app = App()
    print("login admin:", app.login("admin", "s3cret"))
    print("render:", app.render_message("<script>evil()</script>"))
    print("alice reads note 1:", app.read_note(1, "alice"))
