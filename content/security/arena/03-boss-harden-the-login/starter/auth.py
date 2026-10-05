import hashlib
import hmac
import secrets


class AuthError(Exception):
    pass


class WeakPassword(AuthError):
    pass


class LockedOut(AuthError):
    pass


class Accounts:
    def __init__(self):
        self.users = {}
        self.sessions = {}

    def register(self, name, password):
        self.users[name] = password

    def login(self, name, password):
        if name not in self.users:
            raise AuthError("no such user")
        if self.users[name] != password:
            raise AuthError("wrong password")
        token = name + "-token"
        self.sessions[token] = name
        return token

    def unlock(self, name):
        pass

    def whoami(self, token):
        return self.sessions.get(token)

    def logout(self, token):
        del self.sessions[token]
