import asyncio
import urllib.parse
import sys

from http_parsing import read_http_message

request_data = "GET / HTTP/1.0\r\n" "Host: 127.0.0.1\r\n" "Connection: close\r\n" "\r\n"

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

    header, body = await read_http_message(reader)

    writer.write(req.encode())

    print(f"Response Headers >")
    print(header)
    print(f"Response Body >")
    print(body)


url = sys.argv[1]
# url = "http://127.0.0.1:8888"
asyncio.run(http_request(url))
