import asyncio
import json

# fmt: off
HTTP_RESPONSE = (
    f"HTTP/1.0 200 OK\r\n"
    f"Access-Control-Allow-Origin: *\r\n"
    f"Connection: Keep-Alive\r\n"
    f"Content-Encoding: gzip\r\n"
    f"Content-Type: text/html; charset=utf-8\r\n"
    f"Keep-Alive: timeout=5, max=999\r\n"
    f"Server: Apache\r\n"
    f"Content-Length: 5\r\n"
    f"\r\n"
    f"01234"
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


async def handle_http_request(reader, writer):
    addr = writer.get_extra_info("peername")

    print(f"Ready to receive from {addr!r}")

    data = bytearray()
    request_header_data = bytearray()
    request_body_data = bytearray()
    chunk = bytearray()
    chunk_size = 2

    request_header = dict()
    request_body = str()

    # Handle HTTP protocol to get request
    while True:
        chunk = await reader.read(chunk_size)
        data += chunk

        if b"\r\n\r\n" in data:
            body_part: bytearray
            request_header_data, body_part = data.split(b"\r\n\r\n")
            request_header = parse_header_b(request_header_data)

            if "content-length" in request_header:
                body_size = int(request_header["content-length"])
                request_body_data = body_part
                recv_size = len(request_body_data)
                while body_size > recv_size:
                    chunk = await reader.read(chunk_size)
                    request_body_data += chunk
                    data += chunk
                    recv_size += len(chunk)

                assert (
                    len(request_body_data) == body_size
                ), "body size does not match Content-Length!"
                request_body = request_body_data.decode()
                break
            else:
                break

    print(f"Request Headers >")
    print(request_header)
    print(f"Request Body >")
    print(request_body)

    # HTTP handlers
    # response = handle_request(request_header, request_body)

    # print(f"Received {data}")
    message = {"name": "sample", "time": 11111.0, "day": 111, "addr": addr}
    message = json.dumps(message)

    HTTP_RESPONSE = (
        f"HTTP/1.0 200 OK\r\n"
        f"Access-Control-Allow-Origin: *\r\n"
        f"Content-Type: application/json\r\n"
        f"Server: Apache\r\n"
        f"Content-Length: {len(message)}\r\n"
        f"\r\n"
        f"{message}"
    )

    writer.write(HTTP_RESPONSE.encode())
    await writer.drain()

    # TODO: don't close if `connection: keep-alive`
    print("Close the connection")
    writer.close()
    await writer.wait_closed()


async def main():
    server = await asyncio.start_server(handle_http_request, "127.0.0.1", 8888)

    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print(f"Serving on {addrs}")

    async with server:
        await server.serve_forever()


asyncio.run(main())
