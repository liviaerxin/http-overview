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


async def http_request(data):
    reader, writer = await asyncio.open_connection("127.0.0.1", 8888)
    writer.write(data.encode())

    response_header = b""
    while True:
        line = await reader.readline()
        if not line:
            break

        response_header += line

        line = line.decode().rstrip()
        if line:
            print(f"HTTP header> {line}")
        else:
            line
    print(f"response_header:\n {response_header}")


# url = sys.argv[1]
asyncio.run(http_request(HTTP_GET_REQUEST))
