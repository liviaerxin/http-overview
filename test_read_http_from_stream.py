from io import StringIO, BytesIO
from http_parsing import parse_headers_b, parse_headers_s


def test_read_http_headers():
    # fmt: off
    RAW_HTTP_REQUEST = (
        b"GET / HTTP/1.0\r\n"
        b"Host: 127.0.0.1\r\n"
        b"\r\n"
    )
    # fmt: on

    stream_reader = BytesIO(RAW_HTTP_REQUEST)

    data = bytearray()
    headers = bytearray()
    body = bytearray()

    while True:
        line = stream_reader.readline()
        # print(f"HTTP header> {line!r}")

        data += line

        if b"\r\n\r\n" in data:
            headers, _ = data.split(b"\r\n\r\n")

            # print(headers)
            break

    print(f"Headers >")
    print(headers)
    print(f"Body >")
    print(body)


def test_read_http_headers_with_body_by_readline():
    # fmt: off
    RAW_HTTP_REQUEST = (
        b"GET / HTTP/1.0\r\n"
        b"Host: 127.0.0.1\r\n"
        b"Content-Type: text/html; charset=utf-8\r\n"
        b"Content-Length: 10\r\n"
        b"\r\n"
        b"0123456789"
    )
    # fmt: on

    stream_reader = BytesIO(RAW_HTTP_REQUEST)

    data = bytearray()
    headers = bytearray()
    body = bytearray()

    while True:
        line = stream_reader.readline()
        # print(f"HTTP header> {line!r}")

        data += line

        if b"\r\n\r\n" in data:
            headers, body_part = data.split(b"\r\n\r\n")
            parsed_headers = parse_headers_b(headers)
            # print(headers)
            if "content-length" in parsed_headers:
                body_size = int(parsed_headers["content-length"])
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
    print(parsed_headers)
    print(f"Body >")
    print(body)


def test_read_http_headers_with_body_by_chunk():
    # fmt: off
    RAW_HTTP_REQUEST = (
        b"GET / HTTP/1.0\r\n"
        b"Host: 127.0.0.1\r\n"
        b"Content-Type: text/html; charset=utf-8\r\n"
        b"Content-Length: 10\r\n"
        b"\r\n"
        b"0123456789\r\n"
    )
    # fmt: on

    stream_reader = BytesIO(RAW_HTTP_REQUEST)

    data = bytearray()
    header = bytearray()
    body = bytearray()
    chunk_size = 2

    # core loop to get data from socket stream
    while True:
        chunk = stream_reader.read(chunk_size)
        # print(f"HTTP header> {line!r}")

        data += chunk

        if b"\r\n\r\n" in data:
            headers, body_part = data.split(b"\r\n\r\n")
            parsed_headers = parse_headers_b(headers)
            # print(headers)
            if "content-length" in parsed_headers:
                body_size = int(parsed_headers["content-length"])
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
    print(parsed_headers)
    print(f"Body >")
    print(body)
