import asyncio

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


def parse_headers_b(headers_b: bytearray):
    return parse_headers_s(headers_b.decode())


def parse_headers_s(headers_s: str):
    output = {}
    fields = headers_s.split("\r\n")
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


async def read_http_message(reader: asyncio.StreamReader, chunk_size=2):
    data = bytearray()
    headers_data = bytearray()
    body_data = bytearray()
    chunk = bytearray()

    parsed_headers = dict()

    # Handle HTTP protocol to get request
    while True:
        chunk = await reader.read(chunk_size)
        data += chunk

        if b"\r\n\r\n" in data:
            body_part: bytearray
            headers_data, body_part = data.split(b"\r\n\r\n")
            parsed_headers = parse_headers_b(headers_data)

            if "content-length" in parsed_headers:
                body_size = int(parsed_headers["content-length"])
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
                break
            else:
                break

    # Parse body
    body = bytearray()

    return parsed_headers, body_data


async def writer_http_message(data: bytearray, writer: asyncio.StreamWriter):
    writer.write(data)
