import base64
import hmac
import json


class BadToken(Exception):
    """The token is malformed, forged or expired."""


class Expired(BadToken):
    pass


def seal(data, key):
    pass


def unseal(token, key, now):
    pass
