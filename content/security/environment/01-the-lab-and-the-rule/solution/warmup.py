import base64


def reveal(encoded):
    # base64 is an encoding, not a secret: decoding it needs no key, only the
    # knowledge that it is base64 in the first place.
    return base64.b64decode(encoded).decode()


if __name__ == "__main__":
    print(reveal("d2VsY29tZSB0byB0aGUgbGFi"))
