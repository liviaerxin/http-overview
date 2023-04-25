import asyncio
import urllib.parse
import sys

# fmt: off
HTTP_GET_REQUEST = (
    f"GET / HTTP/1.0\r\n"
    f"Host: 127.0.0.1\r\n"
    f"\r\n"
)
# fmt: on

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
    f"0123456789\r\n"
)
# fmt: on


def parse_header_b(header_b: bytearray):
    return parse_header_s(header_b.decode())


def parse_header_s(header_s: str):
    output = {}
    fields = header_s.split("\r\n")
    method, path, _ = fields[0].split(" ", 2)
    output["method"] = method
    output["path"] = path

    fields = fields[1:]  # ignore the GET / HTTP/1.1
    for field in fields:
        if not field:
            continue
        key, value = field.split(":", 1)
        output[key.lower()] = value.lower()
    # print(output)
    return output


async def handle_http_protocol(reader: asyncio.StreamReader):
    data = bytearray()
    header_data = bytearray()
    body_data = bytearray()
    chunk = bytearray()
    chunk_size = 2

    header = dict()
    body = str()

    # Handle HTTP protocol to get request
    while True:
        chunk = await reader.read(chunk_size)
        data += chunk

        if b"\r\n\r\n" in data:
            body_part: bytearray
            header_data, body_part = data.split(b"\r\n\r\n")
            header = parse_header_b(header_data)

            if "content-length" in header:
                body_size = int(header["content-length"])
                body_data = body_part
                recv_size = len(body_data)
                while body_size > recv_size:
                    chunk = await reader.read(chunk_size)
                    body_data += chunk
                    data += chunk
                    recv_size += len(chunk)

                assert (
                    len(body_data) == body_size
                ), "body size does not match Content-Length!"
                body = body_data.decode()
                break
            else:
                break

    return header, body


async def print_http_headers(url):
    url = urllib.parse.urlsplit(url)
    if url.scheme == "https":
        reader, writer = await asyncio.open_connection(url.hostname, 443, ssl=True)
    else:
        reader, writer = await asyncio.open_connection(url.hostname, 80)

    query = (
        f"HEAD {url.path or '/'} HTTP/1.0\r\n",
        f"Host: {url.hostname}\r\n",
        f"\r\n",
    )

    writer.write(query.encode("latin-1"))
    while True:
        line = await reader.readline()
        if not line:
            break

        line = line.decode("latin1").rstrip()
        if line:
            print(f"HTTP header> {line}")

    # Ignore the body, close the socket
    writer.close()
    await writer.wait_closed()


async def http_request(url):
    url = urllib.parse.urlsplit(url)
    if url.scheme == "https":
        reader, writer = await asyncio.open_connection(
            url.hostname, url.port if url.port else 443, ssl=True
        )
    else:
        reader, writer = await asyncio.open_connection(
            url.hostname, url.port if url.port else 80
        )

    # fmt: off
    req = (
        f"GET {url.path or '/'} HTTP/1.0\r\n"
        f"Host: {url.hostname}\r\n"
        f"\r\n"
    )
    # fmt: on

    writer.write(req.encode())

    header, body = await handle_http_protocol(reader)
    print(f"Response Headers >")
    print(header)
    print(f"Response Body >")
    print(body)


# url = sys.argv[1]
url = "http://127.0.0.1:8888"
asyncio.run(http_request(url))
