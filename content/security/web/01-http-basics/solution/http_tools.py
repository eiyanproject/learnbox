def parse_request(raw):
    # The blank line separates head from body. Everything in HTTP hangs off
    # that structure, so splitting on it correctly is the whole parse.
    head, _, body = raw.partition("\r\n\r\n")
    lines = head.split("\r\n")
    method, path, version = lines[0].split(" ", 2)
    headers = {}
    for line in lines[1:]:
        if not line:
            continue
        name, _, value = line.partition(":")
        # Header names are case-insensitive; lower-casing them makes lookups
        # reliable no matter how the client capitalised them.
        headers[name.strip().lower()] = value.strip()
    return {"method": method, "path": path, "version": version,
            "headers": headers, "body": body}


def build_response(status, headers, body=""):
    lines = [f"HTTP/1.1 {status}"]
    for name, value in headers.items():
        lines.append(f"{name}: {value}")
    return "\r\n".join(lines) + "\r\n\r\n" + body


def query_params(path):
    _, _, query = path.partition("?")
    params = {}
    if not query:
        return params
    for pair in query.split("&"):
        key, _, value = pair.partition("=")
        params[key] = value
    return params


if __name__ == "__main__":
    req = "GET /search?q=cat&safe=on HTTP/1.1\r\nHost: example.com\r\n\r\n"
    print(parse_request(req))
    print(query_params("/search?q=cat&safe=on"))
