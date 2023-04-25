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


def parse_headers(headers: str):
    fields = headers.split("\r\n")
    fields = fields[1:]  # ignore the GET / HTTP/1.1
    output = {}
    for field in fields:
        if not field:
            continue
        key, value = field.split(":", 1)
        key = key.lower()
        output[key] = value
    return output


async def handle_http_request(reader, writer):
    addr = writer.get_extra_info("peername")

    print(f"Ready to receive from {addr!r}")

    data = bytearray()
    header = bytearray()
    body = bytearray()
    chunk_size = 2

    # core loop to get data from socket stream
    while True:
        chunk = await reader.read(chunk_size)
        data += chunk

        if b"\r\n\r\n" in data:
            header, body_part = data.split(b"\r\n\r\n")
            headers = parse_headers(header.decode())

            if "content-length" in headers:
                body_size = int(headers["content-length"])
                body_size = body_size
                body += body_part

                while body_size > len(body):
                    chunk = await reader.read(chunk_size)
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

    # print(f"Received {data}")
    message = {"name": "sample", "time": 11111.0, "day": 111}
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
