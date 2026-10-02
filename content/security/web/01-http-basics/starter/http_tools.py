def parse_request(raw):
    pass


def build_response(status, headers, body=""):
    pass


def query_params(path):
    pass


if __name__ == "__main__":
    req = "GET /search?q=cat&safe=on HTTP/1.1\r\nHost: example.com\r\n\r\n"
    print(parse_request(req))
    print(query_params("/search?q=cat&safe=on"))
