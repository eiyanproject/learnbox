import hashlib
import hmac
import secrets


class AuthError(Exception):
    pass


class WeakPassword(AuthError):
    pass


class LockedOut(AuthError):
    pass


MAX_FAILURES = 5


def digest(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)


class Accounts:
    def __init__(self):
        self.users = {}
        self.sessions = {}
        self.failures = {}

    def register(self, name, password):
        if name in self.users:
            raise AuthError("name taken")
        if len(password) < 10:
            raise WeakPassword("at least 10 characters")
        salt = secrets.token_bytes(16)
        self.users[name] = (salt, digest(password, salt))

    def login(self, name, password):
        if name not in self.users:
            raise AuthError("invalid credentials")
        if self.failures.get(name, 0) >= MAX_FAILURES:
            raise LockedOut(name)
        salt, stored = self.users[name]
        if not hmac.compare_digest(digest(password, salt), stored):
            self.failures[name] = self.failures.get(name, 0) + 1
            raise AuthError("invalid credentials")
        self.failures[name] = 0
        token = secrets.token_hex(16)
        self.sessions[token] = name
        return token

    def unlock(self, name):
        self.failures[name] = 0

    def whoami(self, token):
        return self.sessions.get(token)

    def logout(self, token):
        self.sessions.pop(token, None)
