import base64
import hmac
import json


class BadToken(Exception):
    """The token is malformed, forged or expired."""


class Expired(BadToken):
    pass


def signature(payload, key):
    return hmac.new(key, payload.encode(), "sha256").hexdigest()


def seal(data, key):
    raw = json.dumps(data, sort_keys=True).encode()
    payload = base64.urlsafe_b64encode(raw).decode()
    return payload + "." + signature(payload, key)


def unseal(token, key, now):
    parts = token.split(".")
    if len(parts) != 2:
        raise BadToken("expected payload.signature")
    payload, given = parts
    if not hmac.compare_digest(signature(payload, key).encode(), given.encode()):
        raise BadToken("bad signature")
    try:
        data = json.loads(base64.urlsafe_b64decode(payload.encode()))
    except ValueError as err:
        raise BadToken("unreadable payload") from err
    if not isinstance(data, dict):
        raise BadToken("payload is not an object")
    if "exp" in data and now >= data["exp"]:
        raise Expired("expired")
    return data
