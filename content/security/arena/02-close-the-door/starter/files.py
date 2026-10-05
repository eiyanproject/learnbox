import posixpath


class Forbidden(Exception):
    """The request points outside the folder being served."""


def resolve(base, requested):
    return posixpath.join(base, requested)
