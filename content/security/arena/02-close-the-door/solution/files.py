import posixpath


class Forbidden(Exception):
    """The request points outside the folder being served."""


def resolve(base, requested):
    if not requested or "\x00" in requested or "\\" in requested:
        raise Forbidden(requested)
    if requested.startswith("/"):
        raise Forbidden(requested)
    base = posixpath.normpath(base)
    full = posixpath.normpath(posixpath.join(base, requested))
    # The separator matters: /srv/files-private starts with /srv/files too.
    if not full.startswith(base.rstrip("/") + "/"):
        raise Forbidden(requested)
    return full
