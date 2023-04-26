from http_parsing import parse_headers_b, parse_headers_s


def test_parse_headers():
    # fmt: off
    HTTP_REQUEST = (
        b"GET / HTTP/1.0\r\n"
        b"Host: 127.0.0.1\r\n"
        b"\r\n"
    )
    # fmt: on
    headers = parse_headers_b(HTTP_REQUEST)
    print(headers)


def test_parse_headers_1():
    # fmt: off
    HTTP_REQUEST = (
        b"GET / HTTP/1.0\r\n"
        b"Host: 127.0.0.1"
    )
    # fmt: on
    headers = parse_headers_b(HTTP_REQUEST)
    print(headers)
