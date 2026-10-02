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
        # Parameterised: user input is data, never part of the query text.
        row = self.db.execute(
            "SELECT username FROM users WHERE username=? AND password=?",
            (user, pw),
        ).fetchone()
        return row[0] if row else None

    def render_message(self, text):
        # Escaped on output: a script payload becomes inert text.
        return f"<li class='msg'>{html.escape(text)}</li>"

    def read_note(self, note_id, user):
        # Authorisation: the note is returned only to its owner.
        note = self.notes.get(note_id)
        if note is None or note["owner"] != user:
            return None
        return note["text"]


if __name__ == "__main__":
    app = App()
    print("login admin:", app.login("admin", "s3cret"))
    print("render:", app.render_message("<script>evil()</script>"))
    print("alice reads note 1:", app.read_note(1, "alice"))
