from io import StringIO, BytesIO

# fmt: off
HTTP_RESPONSE = (
    f"HTTP/1.0 200 OK\r\n"
    f"Access-Control-Allow-Origin: *\r\n"
    f"Connection: Keep-Alive\r\n"
    f"Content-Encoding: gzip\r\n"
    f"Content-Type: text/html; charset=utf-8\r\n"
    f"Keep-Alive: timeout=5, max=999\r\n"
    f"Server: Apache\r\n"
    f"Content-Length: 10\r\n"
    f"\r\n"
    f"0123456789"
)
# fmt: on


def parse_headers(headers: str):
    fields = headers.split("\r\n")
    fields = fields[1:]  # ignore the GET / HTTP/1.1
    output = {}
    for field in fields:
        if not field:
            continue
        key, value = field.split(":", 1)
        output[key] = value
    # print(output)
    return output


def test_http_headers_eof():
    # fmt: off
    HTTP_REQUEST = (
        f"GET / HTTP/1.0\r\n"
        f"Host: 127.0.0.1\r\n"
        f"\r\n"
    )
    # fmt: on

    stream_reader = StringIO(HTTP_REQUEST)

    data = str()
    header = str()
    body = str()

    while True:
        line = stream_reader.readline()
        # print(f"HTTP header> {line!r}")

        data += line

        if "\r\n\r\n" in data:
            header, _ = data.split("\r\n\r\n")

            headers = parse_headers(header)

            # print(headers)
            break

    print(f"Headers >")
    print(headers)
    print(f"Body >")
    print(body)


def test_http_headers_with_body_eof():
    # fmt: off
    HTTP_REQUEST = (
        f"GET / HTTP/1.0\r\n"
        f"Host: 127.0.0.1\r\n"
        f"Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: 10\r\n"
        f"\r\n"
        f"0123456789\r\n"
    )
    # fmt: on

    stream_reader = StringIO(HTTP_REQUEST)

    data = str()
    header = str()
    body = str()

    while True:
        line = stream_reader.readline()
        # print(f"HTTP header> {line!r}")

        data += line

        if "\r\n\r\n" in data:
            header, body_part = data.split("\r\n\r\n")
            headers = parse_headers(header)
            # print(headers)
            if "Content-Length" in headers:
                body_size = int(headers["Content-Length"])
                body_size = body_size
                body += body_part
                while body_size > len(body):
                    line = stream_reader.readline()
                    body += line
                    data += line

                assert (
                    len(body) == body_size
                ), "body size does not match Content-Length!"
                break
            else:
                break

    print(f"Headers >")
    print(headers)
    print(f"Body >")
    print(body)


def test_http_headers_with_body_generic():
    # fmt: off
    HTTP_REQUEST = (
        f"GET / HTTP/1.0\r\n"
        f"Host: 127.0.0.1\r\n"
        f"Content-Type: text/html; charset=utf-8\r\n"
        f"Content-Length: 10\r\n"
        f"\r\n"
        f"0123456789\r\n"
    )
    # fmt: on

    stream_reader = StringIO(HTTP_REQUEST)

    data = str()
    header = str()
    body = str()
    chunk_size = 2

    # core loop to get data from socket stream
    while True:
        chunk = stream_reader.read(chunk_size)
        # print(f"HTTP header> {line!r}")

        data += chunk

        if "\r\n\r\n" in data:
            header, body_part = data.split("\r\n\r\n")
            headers = parse_headers(header)
            # print(headers)
            if "Content-Length" in headers:
                body_size = int(headers["Content-Length"])
                body_size = body_size + 2
                body += body_part
                while body_size > len(body):
                    chunk = stream_reader.read(chunk_size)
                    body += chunk
                    data += chunk

                assert (
                    len(body) == body_size
                ), "body size does not match Content-Length!"
                break
            else:
                break

    print(f"Headers >")
    print(headers)
    print(f"Body >")
    print(body)
