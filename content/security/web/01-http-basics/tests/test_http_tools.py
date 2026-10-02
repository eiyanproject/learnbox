from http_tools import parse_request, build_response, query_params

REQ = ("POST /login HTTP/1.1\r\n"
       "Host: example.com\r\n"
       "Content-Type: application/x-www-form-urlencoded\r\n"
       "\r\n"
       "user=admin&pw=secret")


def test_parse_method_path_version():
    r = parse_request(REQ)
    assert r["method"] == "POST"
    assert r["path"] == "/login"
    assert r["version"] == "HTTP/1.1"


def test_parse_headers_lowercased():
    r = parse_request(REQ)
    assert r["headers"]["host"] == "example.com"
    assert r["headers"]["content-type"] == "application/x-www-form-urlencoded"


def test_parse_body():
    assert parse_request(REQ)["body"] == "user=admin&pw=secret"


def test_parse_handles_mixed_case_header():
    r = parse_request("GET / HTTP/1.1\r\nX-Custom-Header: Yes\r\n\r\n")
    assert r["headers"]["x-custom-header"] == "Yes"


def test_parse_no_body():
    r = parse_request("GET / HTTP/1.1\r\nHost: x\r\n\r\n")
    assert r["body"] == ""


def test_build_response_status_line():
    out = build_response("200 OK", {"Content-Type": "text/html"}, "<p>hi</p>")
    assert out.startswith("HTTP/1.1 200 OK\r\n")


def test_build_response_round_trips_through_parse():
    out = build_response("200 OK", {"X-Test": "yes"}, "body text")
    # Response and request share the head/body structure, so the parser reads it.
    r = parse_request(out.replace("HTTP/1.1 200 OK", "GET / HTTP/1.1", 1))
    assert r["headers"]["x-test"] == "yes"
    assert r["body"] == "body text"


def test_build_response_blank_line_before_body():
    out = build_response("404 Not Found", {}, "gone")
    assert "\r\n\r\n" in out
    assert out.endswith("gone")


def test_query_params_basic():
    assert query_params("/search?q=cat&safe=on") == {"q": "cat", "safe": "on"}


def test_query_params_single():
    assert query_params("/p?id=42") == {"id": "42"}


def test_query_params_none():
    assert query_params("/plain/path") == {}


def test_query_params_empty_value():
    assert query_params("/x?flag=") == {"flag": ""}
