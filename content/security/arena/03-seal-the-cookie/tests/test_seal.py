import base64
import hmac
import inspect
import json

import pytest

import seal as module
from seal import BadToken, Expired, seal, unseal

KEY = b"correct horse battery staple"
DATA = {"user": "ana", "admin": False}


def encode(obj):
    return base64.urlsafe_b64encode(json.dumps(obj, sort_keys=True).encode()).decode()


def sign(payload, key=KEY):
    return hmac.new(key, payload.encode(), "sha256").hexdigest()


def test_the_token_has_the_documented_shape():
    token = seal(DATA, KEY)
    assert isinstance(token, str)
    payload, signature = token.split(".")
    assert payload == encode(DATA)
    assert signature == sign(payload)


def test_round_trip():
    assert unseal(seal(DATA, KEY), KEY, now=0) == DATA


def test_key_order_does_not_change_the_token():
    assert seal({"a": 1, "b": 2}, KEY) == seal({"b": 2, "a": 1}, KEY)


def test_a_different_key_gives_a_different_signature():
    assert seal(DATA, KEY) != seal(DATA, b"another key")


def test_the_wrong_key_is_refused():
    with pytest.raises(BadToken):
        unseal(seal(DATA, KEY), b"another key", now=0)


def test_an_edited_payload_is_refused():
    _, signature = seal(DATA, KEY).split(".")
    forged = encode({"user": "ana", "admin": True}) + "." + signature
    with pytest.raises(BadToken):
        unseal(forged, KEY, now=0)


def test_an_edited_signature_is_refused():
    payload, signature = seal(DATA, KEY).split(".")
    flipped = ("0" if signature[0] != "0" else "1") + signature[1:]
    with pytest.raises(BadToken):
        unseal(payload + "." + flipped, KEY, now=0)


@pytest.mark.parametrize("signature", ["", "none", "0" * 64])
def test_a_missing_or_made_up_signature_is_refused(signature):
    with pytest.raises(BadToken):
        unseal(encode({"user": "root", "admin": True}) + "." + signature, KEY, now=0)


def test_a_signature_made_with_an_empty_key_is_refused():
    payload = encode({"user": "root", "admin": True})
    with pytest.raises(BadToken):
        unseal(payload + "." + sign(payload, b""), KEY, now=0)


@pytest.mark.parametrize("token", ["", "abc", "a.b.c", ".", "..", "no dots at all"])
def test_malformed_tokens_are_refused(token):
    with pytest.raises(BadToken):
        unseal(token, KEY, now=0)


def test_a_correctly_signed_payload_that_is_not_json_is_refused():
    payload = base64.urlsafe_b64encode(b"not json").decode()
    with pytest.raises(BadToken):
        unseal(payload + "." + sign(payload), KEY, now=0)


def test_a_correctly_signed_payload_that_is_not_base64_is_refused():
    payload = "!!!not-base64!!!"
    with pytest.raises(BadToken):
        unseal(payload + "." + sign(payload), KEY, now=0)


def test_a_correctly_signed_payload_that_is_not_an_object_is_refused():
    payload = encode([1, 2, 3])
    with pytest.raises(BadToken):
        unseal(payload + "." + sign(payload), KEY, now=0)


def test_expiry():
    token = seal({"user": "ana", "exp": 1000}, KEY)
    assert unseal(token, KEY, now=999) == {"user": "ana", "exp": 1000}
    with pytest.raises(Expired):
        unseal(token, KEY, now=1000)
    with pytest.raises(Expired):
        unseal(token, KEY, now=5000)


def test_expired_is_a_bad_token():
    assert issubclass(Expired, BadToken)
    with pytest.raises(BadToken):
        unseal(seal({"exp": 1}, KEY), KEY, now=2)


def test_no_expiry_means_no_expiry():
    assert unseal(seal(DATA, KEY), KEY, now=10**12) == DATA


def test_an_expired_token_with_a_bad_signature_is_just_bad():
    payload = encode({"user": "ana", "exp": 1})
    with pytest.raises(BadToken) as err:
        unseal(payload + "." + "0" * 64, KEY, now=2)
    assert not isinstance(err.value, Expired), "check the signature before trusting anything in the payload"


def test_signatures_are_compared_in_constant_time():
    assert "compare_digest" in inspect.getsource(module), "compare signatures with hmac.compare_digest"


def test_unicode_survives():
    data = {"name": "Zoë", "city": "東京"}
    assert unseal(seal(data, KEY), KEY, now=0) == data
