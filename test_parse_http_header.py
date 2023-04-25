def parse_headers(headers: str):
    output = {}
    fields = headers.split("\r\n")
    method, path, _ = fields[0].split(" ", 2)
    output["method"] = method
    output["path"] = path

    fields = fields[1:]  # ignore the GET / HTTP/1.1
    for field in fields:
        if not field:
            continue
        key, value = field.split(":", 1)
        output[key] = value
    # print(output)
    return output


def test_parse_headers():
    # fmt: off
    HTTP_REQUEST = (
        f"GET / HTTP/1.0\r\n"
        f"Host: 127.0.0.1\r\n"
        f"\r\n"
    )
    # fmt: on
    headers = parse_headers(HTTP_REQUEST)
    print(headers)


def test_parse_headers_1():
    # fmt: off
    HTTP_REQUEST = (
        f"GET / HTTP/1.0\r\n"
        f"Host: 127.0.0.1"
    )
    # fmt: on
    headers = parse_headers(HTTP_REQUEST)
    print(headers)
