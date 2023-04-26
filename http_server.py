import asyncio
import json

from http_parsing import read_http_message

# fmt: off
HTTP_RESPONSE = (
    b"HTTP/1.0 200 OK\r\n"
    b"Access-Control-Allow-Origin: *\r\n"
    b"Connection: Keep-Alive\r\n"
    b"Content-Encoding: gzip\r\n"
    b"Content-Type: text/html; charset=utf-8\r\n"
    b"Keep-Alive: timeout=5, max=999\r\n"
    b"Server: Apache\r\n"
    b"Content-Length: 5\r\n"
    b"\r\n"
    b"01234"
)
# fmt: on


def mock_handler(request_header: dict, request_body: bytearray):
    message = {"name": "sample", "time": 11111.0, "day": 111}
    message = json.dumps(message)

    return message


async def handle_http_request(reader, writer):
    addr = writer.get_extra_info("peername")

    print(f"Ready to receive from {addr!r}")

    # 1. Handle request
    while True:
        chunk_size = 2
        request_parsed_headers, request_body = await read_http_message(
            reader, chunk_size
        )

        print(f"Request Headers >")
        print(request_parsed_headers)
        print(f"Request Body >")
        print(request_body)

        # 2. Handle request into HTTP handlers
        # response = handle_request(request_header, request_body)

        # print(f"Received {data}")

        # 3. Handle response
        message = mock_handler(request_parsed_headers, request_body)

        HTTP_RESPONSE = (
            f"HTTP/1.0 200 OK\r\n"
            f"Access-Control-Allow-Origin: *\r\n"
            f"Content-Type: application/json\r\n"
            f"Server: Apache\r\n"
            f"Client: {addr}\r\n"
            f"Content-Length: {len(message)}\r\n"
            f"\r\n"
            f"{message}"
        )

        writer.write(HTTP_RESPONSE.encode())
        await writer.drain()

        # TODO: don't close if `connection: keep-alive`
        if "connection" not in request_parsed_headers:
            request_parsed_headers["connection"] = "keep-alive"

        if request_parsed_headers["connection"] == "close":
            break
        elif request_parsed_headers["connection"] == "keep-alive":
            print("Keep the connection")
            pass
        else:
            print("Keep the connection")
            pass

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
